# Dictionary of all possible GTFS files and their fields with datatypes
GTFS_FILE_FIELD_TYPE_MAPPING = {
    "agency.txt": {
        "agency_id": "string",
        "agency_name": "string",
        "agency_url": "string",
        "agency_timezone": "string",
        "agency_lang": "string",
        "agency_phone": "string",
        "agency_fare_url": "string",
        "agency_email": "string"
    },
    "stops.txt": {
        "stop_id": "string",
        "stop_code": "string",
        "stop_name": "string",
        "tts_stop_name": "string",
        "stop_desc": "string",
        "stop_lat": "float",
        "stop_lon": "float",
        "zone_id": "string",
        "stop_url": "string",
        "location_type": "integer",
        "parent_station": "string",
        "stop_timezone": "string",
        "wheelchair_boarding": "integer",
        "level_id": "string",
        "platform_code": "string"
    },
    "routes.txt": {
        "route_id": "string",
        "agency_id": "string",
        "route_short_name": "string",
        "route_long_name": "string",
        "route_desc": "string",
        "route_type": "integer",
        "route_url": "string",
        "route_color": "string",
        "route_text_color": "string",
        "route_sort_order": "integer",
        "continuous_pickup": "integer",
        "continuous_drop_off": "integer",
        "network_id": "string"
    },
    "trips.txt": {
        "route_id": "string",
        "service_id": "string",
        "trip_id": "string",
        "trip_headsign": "string",
        "trip_short_name": "string",
        "direction_id": "integer",
        "block_id": "string",
        "shape_id": "string",
        "wheelchair_accessible": "integer",
        "bikes_allowed": "integer"
    },
    "stop_times.txt": {
        "trip_id": "string",
        "arrival_time": "time",
        "departure_time": "time",
        "stop_id": "string",
        "location_group_id": "string",
        "location_id": "string",
        "stop_sequence": "integer",
        "stop_headsign": "string",
        "start_pickup_drop_off_window": "time",
        "end_pickup_drop_off_window": "time",
        "pickup_type": "integer",
        "drop_off_type": "integer",
        "continuous_pickup": "integer",
        "continuous_drop_off": "integer",
        "shape_dist_traveled": "float",
        "timepoint": "integer",
        "pickup_booking_rule_id": "string",
        "drop_off_booking_rule_id": "string"
    },
    "calendar.txt": {
        "service_id": "string",
        "monday": "integer",
        "tuesday": "integer",
        "wednesday": "integer",
        "thursday": "integer",
        "friday": "integer",
        "saturday": "integer",
        "sunday": "integer",
        "start_date": "date",
        "end_date": "date"
    },
    "calendar_dates.txt": {
        "service_id": "string",
        "date": "date",
        "exception_type": "integer"
    },
    "fare_attributes.txt": {
        "fare_id": "string",
        "price": "float",
        "currency_type": "string",
        "payment_method": "integer",
        "transfers": "integer",
        "agency_id": "string",
        "transfer_duration": "integer"
    },
    "fare_rules.txt": {
        "fare_id": "string",
        "route_id": "string",
        "origin_id": "string",
        "destination_id": "string",
        "contains_id": "string"
    },
    "timeframes.txt": {
        "timeframe_group_id": "string",
        "start_time": "time",
        "end_time": "time",
        "service_id": "string"
    },
    "fare_media.txt": {
        "fare_media_id": "string",
        "fare_media_name": "string",
        "fare_media_type": "integer"
    },
    "fare_products.txt": {
        "fare_product_id": "string",
        "fare_product_name": "string",
        "fare_media_id": "string",
        "amount": "float",
        "currency": "string"
    },
    "fare_leg_rules.txt": {
        "leg_group_id": "string",
        "network_id": "string",
        "from_area_id": "string",
        "to_area_id": "string",
        "fare_product_id": "string",
        "from_timeframe_group_id": "string",
        "to_timeframe_group_id": "string",
        "rule_priority": "integer"
    },
    "fare_transfer_rules.txt": {
        "from_leg_group_id": "string",
        "to_leg_group_id": "string",
        "transfer_count": "integer",
        "duration_limit": "integer",
        "duration_limit_type": "string",
        "fare_transfer_type": "string",
        "fare_product_id": "string"
    },
    "areas.txt": {
        "area_id": "string",
        "area_name": "string"
    },
    "stop_areas.txt": {
        "area_id": "string",
        "stop_id": "string"
    },
    "networks.txt": {
        "network_id": "string",
        "network_name": "string"
    },
    "route_networks.txt": {
        "route_id": "string",
        "network_id": "string"
    },
    "shapes.txt": {
        "shape_id": "string",
        "shape_pt_lat": "float",
        "shape_pt_lon": "float",
        "shape_pt_sequence": "integer",
        "shape_dist_traveled": "float"
    },
    "frequencies.txt": {
        "trip_id": "string",
        "start_time": "time",
        "end_time": "time",
        "headway_secs": "integer",
        "exact_times": "integer"
    },
    "transfers.txt": {
        "from_stop_id": "string",
        "to_stop_id": "string",
        "transfer_type": "integer",
        "min_transfer_time": "integer"
    },
    "pathways.txt": {
        "pathway_id": "string",
        "from_stop_id": "string",
        "to_stop_id": "string",
        "pathway_mode": "integer",
        "is_bidirectional": "integer",
        "length": "float",
        "traversal_time": "integer",
        "stair_count": "integer",
        "max_slope": "float",
        "min_width": "float",
        "signposted_as": "string",
        "reversed_signposted_as": "string"
    },
    "levels.txt": {
        "level_id": "string",
        "level_index": "float",
        "level_name": "string"
    },
    "location_groups.txt": {
        "location_group_id": "string",
        "location_group_name": "string",
        "location_group_type": "string"
    },
    "location_group_stops.txt": {
        "location_group_id": "string",
        "stop_id": "string"
    },
    "locations.geojson": {
        "type": "string",
        "features": "array of objects"  # This is a special case, it's a GeoJSON file with `Feature` objects
    },
    "booking_rules.txt": {
        "booking_rule_id": "string",
        "booking_type": "string",
        "prior_notice_duration_min": "integer",
        "prior_notice_duration_max": "integer",
        "prior_notice_last_day": "date",
        "prior_notice_last_time": "time",
        "prior_notice_start_day": "date",
        "prior_notice_start_time": "time",
        "prior_notice_service_id": "string",
        "message": "string",
        "pickup_message": "string",
        "drop_off_message": "string",
        "phone_number": "string",
        "info_url": "string",
        "booking_url": "string"
    },
    "translations.txt": {
        "table_name": "string",
        "field_name": "string",
        "language": "string",
        "translation": "string",
        "record_id": "string",
        "record_sub_id": "string",
        "field_value": "string"
    },
    "feed_info.txt": {
        "feed_publisher_name": "string",
        "feed_publisher_url": "string",
        "feed_lang": "string",
        "default_lang": "string",
        "feed_start_date": "date",
        "feed_end_date": "date",
        "feed_version": "string",
        "feed_contact_email": "string",
        "feed_contact_url": "string"
    },
    "attributions.txt": {
        "attribution_id": "string",
        "agency_id": "string",
        "route_id": "string",
        "trip_id": "string",
        "organization_name": "string",
        "is_producer": "integer",
        "is_operator": "integer",
        "is_authority": "integer",
        "attribution_url": "string",
        "attribution_email": "string",
        "attribution_phone": "string"
    }
}