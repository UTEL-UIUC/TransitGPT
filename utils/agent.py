import streamlit as st
import logging
import os
from logging.handlers import RotatingFileHandler
from prompts.all_prompts import (
    FINAL_LLM_SYSTEM_PROMPT,
    FINAL_LLM_USER_PROMPT,
    RETRY_PROMPT,
)
from utils.constants import LOG_FILE
from typing import List, Dict, Any, Tuple
from utils.helper import summarize_large_output
from utils.llm_client import OpenAIClient, GroqClient, AnthropicClient
from utils.data_models import ChatInteraction


class LLMAgent:
    def __init__(self, evaluator, max_retry=3, max_chars=12000, max_rows=50):
        self.evaluator = evaluator
        self.max_retry = max_retry
        self.max_chars = max_chars
        self.max_rows = max_rows
        self.logger = self._setup_logger(LOG_FILE)
        self.clients = {
            "gpt": OpenAIClient(),
            "llama": GroqClient(),
            "claude": AnthropicClient(),
        }
        self.last_response = None
        self.chat_history = []
        self.model = None
        self.result = None
        self.distance_units = "Meters"

    def _setup_logger(self, log_file):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Create file handler which logs even debug messages
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)

        # Create console handler with a higher severity log level
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)

        # Create formatter and add it to the handlers
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add the handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    @staticmethod
    def get_client_key(model):
        if model.startswith("claude"):
            return "claude"
        if model.startswith("gpt"):
            return "gpt"
        return "llama"

    def create_messages(
        self, system_prompt: str, user_prompt: str, model: str
    ) -> List[Dict[str, str]]:
        messages = []
        for interaction in self.chat_history:
            messages.append({"role": "user", "content": interaction.user_prompt})
            messages.append(
                {"role": "assistant", "content": interaction.assistant_response}
            )
        messages.append({"role": "user", "content": user_prompt})
        if not model.startswith("claude"):
            messages.insert(0, {"role": "system", "content": system_prompt})
        return messages

    def update_chat_history(
        self, system_prompt: str, user_prompt: str, response: str
    ) -> None:
        interaction = ChatInteraction(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            assistant_response=response,
        )
        self.chat_history.append(interaction)

    def log_llm_interaction(self, messages: List, response: str) -> None:
        self.logger.info(f"Calling LLM with following messages:\n {messages}")
        self.logger.info(f"Response from LLM: {response}")

    def call_llm(self, system_prompt, user_prompt, model):
        self.model = model
        messages = self.create_messages(system_prompt, user_prompt, model)

        client = self.clients[self.get_client_key(model)]
        response, call_success = client.call(model, messages, system_prompt)

        if not call_success:
            self.logger.error(f"LLM call failed: {response}")
        else:
            self.last_response = response
            self.update_chat_history(system_prompt, user_prompt, response)
            self.log_llm_interaction(messages, response)

        return response, call_success

    def evaluate(self, llm_response):
        self.logger.info("Evaluating code from LLM response")
        result, success, error, only_text = self.evaluator.evaluate(llm_response)
        if self.chat_history:
            self.chat_history[-1].evaluation_result = result
            self.chat_history[-1].code_success = success
            self.chat_history[-1].error_message = error
        return result, success, error, only_text

    def evaluate_with_retry(
        self, model: str, llm_response: str
    ) -> Tuple[Any, bool, str, bool, str]:
        call_success = True
        for retry in range(self.max_retry):
            if call_success:
                result, success, error, only_text = self.evaluate(llm_response)
                if success:
                    return result, success, error, only_text, llm_response
            st.write(f"Something wasn't right, retrying: attempt {retry + 1}")
            self.logger.info(
                f"Evaluation failed with error: {error}. Retrying attempt {retry + 1}"
            )
            llm_response, call_success = self.call_llm_retry(model, error)
        return None, False, "Evaluation failed after max retries", False, llm_response

    def get_retry_messages(self, error: str) -> List[Dict[str, str]]:
        messages = []
        for interaction in self.chat_history:
            messages.append({"role": "user", "content": interaction.user_prompt})
            messages.append(
                {"role": "assistant", "content": interaction.assistant_response}
            )
            if interaction.error_message:
                messages.append(
                    {"role": "user", "content": f"Error: {interaction.error_message}"}
                )
        messages.append({"role": "user", "content": RETRY_PROMPT.format(error=error)})
        return messages

    def call_llm_retry(self, model: str, error: str) -> str:
        self.model = model
        self.logger.info(f"Retrying LLM call with model: {model}")

        messages = self.get_retry_messages(error)
        system_prompt = self.chat_history[0].system_prompt if self.chat_history else ""
        client = self.clients[self.get_client_key(model)]
        response, call_success = client.call(model, messages, system_prompt)

        self.logger.info(f"LLM Response: {response}")
        return response, call_success

    def call_final_llm(self):
        system_prompt = FINAL_LLM_SYSTEM_PROMPT
        last_interaction = self.chat_history[-1] if self.chat_history else None

        if not last_interaction:
            self.logger.warning("No interactions in chat history for final LLM call")
            return "No previous interaction available."
        # Additional check to ensure that large dataframes are not passed to the LLM
        summarized_evaluation = summarize_large_output(
            last_interaction.evaluation_result, self.max_rows, self.max_chars
        )
        user_prompt = FINAL_LLM_USER_PROMPT.format(
            question=last_interaction.user_prompt,
            response=last_interaction.assistant_response,
            evaluation=summarized_evaluation,
            success=last_interaction.code_success,
            error=last_interaction.error_message,
        )
        # Hardcoded model for final LLM call
        model = "gpt-4o-mini"
        messages = self.create_messages(system_prompt, user_prompt, model)

        client = self.clients["gpt"]
        response = client.call(model, messages)

        self.logger.info("Final response from LLM:\n %s", response)
        return response

    def reset(self):
        self.last_response = None
        self.chat_history = []
        self.model = None
        self.result = None
