with

int_networkrail__movements_companies_joined as (

    select * from {{ ref('int_networkrail__movements_companies_joined') }}

)

, final as (

    select
        event_type
        , gbtt_timestamp_utc
        , original_loc_stanox
        , planned_timestamp_utc
        , timetable_variation
        , original_loc_timestamp_utc
        , current_train_id
        , delay_monitoring_point
        , next_report_run_time
        , reporting_stanox
        , actual_timestamp_utc
        , correction_ind
        , event_source
        , train_file_address
        , platform
        , division_code
        , train_terminated
        , train_id
        , offroute_ind
        , variation_status
        , train_service_code
        , toc_id
        , company_name
        , loc_stanox
        , auto_expected
        , direction_ind
        , route
        , planned_event_type
        , next_report_stanox
        , line_ind

    from int_networkrail__movements_companies_joined

)

select * from final