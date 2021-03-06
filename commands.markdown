
Some Commands
-------------

::

    devices/
      SyncCommand
      ComLink2/
        CMD_READ_STATUS = 3;
        CMD_READ_PRODUCT_INFO = 4;
        CMD_READ_INTERFACE_STATS = 5;
        CMD_READ_SIGNAL_STRENGTH = 6;
        CMD_READ_DATA = 12;
      LSMeter/
        LEN_READ_CLOCK = 50;
        IO_DELAY_READ_RETRY_MS = 10000;
      LSOneTouchUltraMini
        READ_TIMEOUT_MS = 500
      LSOneTouchUltraSmart
        CMD_READ_CLOCK = "DMF\r";
        READ_TO_MS = 1500;

      MMMeter/
        CMD_READ_CLOCK = 160;
        CMD_READ_SETTINGS = 162;
        CMD_READ_GLUCOSE_DATA = 128;
        LEN_READ_CLOCK = 28;
        LEN_READ_SETTINGS = 72;
        LEN_READ_GLUCOSE_DATA = 44;
        READ_TO_MS = 2500;
        READ_DATA_OFFSET = 0;
        READ_MEM_DATA_OFFSET = 2;
        MAX_READ_BYTES = 250;
      MMPump/
       WRITE_DELAY_MS = 3;

      MMPump508/
        CMD_READ_RTC = 32;
        CMD_READ_PUMP_ID = 33;
        CMD_READ_FIRMWARE_VER = 37;
        CMD_READ_ERROR_STATUS = 38;
        CMD_READ_REMOTE_CTRL_ID = 46;
        REC_SIZE_READ_PUMP_ID = 10;
        REC_SIZE_READ_FIRMWARE_VER = 8;
        REC_SIZE_READ_RTC = 7;
        CMD_READ_BATTERY_STATUS = 34;
        CMD_READ_REMAINING_INSULIN = 35;
        CMD_READ_BOLUS_HISTORY = 39;
        CMD_READ_DAILY_TOTALS = 40;
        CMD_READ_PRIME_BOLUSES = 41;
        CMD_READ_ALARMS = 42;
        CMD_READ_PROFILE_SETS = 43;
        CMD_READ_USER_EVENTS = 44;
        CMD_READ_128K_MEM = 55;
        CMD_READ_256K_MEM = 56;
        CMD_READ_TEMP_BASAL = 64;
        CMD_READ_TODAYS_TOTALS = 65;
        CMD_READ_STD_PROFILES = 66;
        CMD_READ_A_PROFILES = 67;
        CMD_READ_B_PROFILES = 68;
        REC_SIZE_READ_PUMP_ID = 10;
        REC_SIZE_READ_FIRMWARE_VER = 8;
        REC_SIZE_READ_RTC = 7;
        REC_SIZE_READ_TODAYS_TOTAL = 4;
        REC_SIZE_READ_TEMP_BASAL = 4;
        REC_SIZE_READ_CURR_SETTINGS1 = 28;
        REC_SIZE_READ_CURR_SETTINGS2 = 26;
        REC_SIZE_READ_CURR_SETTINGS3 = 4;
        REC_SIZE_READ_CURR_SETTINGS4 = 2;

      MMPump511/
        SuspendResume        = 77;
        PushKeypad           = 91;
        PowerCTRL            = 93;
        ReadRTC              = 112;
        ReadPumpId           = 113;
        ReadBatteryStatus    = 114;
        ReadRemainingInsulin = 115;
        ReadFirmwareVersion  = 116;
        ReadErrorStatus      = 117;
        ReadRadioCtrlACL     = 118;
        ReadBasalTemp        = 120;
        ReadTotalsToday      = 121;
        ReadProfiles_STD     = 122;
        ReadProfiles_A       = 123;
        ReadProfiles_B       = 124;
        ReadSettings         = 127;
        ReadHistoryData      = 128;
        ReadPumpStatus       = 131;
        ReadPumpTrace        = 163;
        ReadDetailTrace      = 164;
        ReadNewTraceAlarm    = 166;
        ReadOldTraceAlarm    = 167;

      MMPump512/ # test pump is a 512
        CMD_READ_SETTINGS = 145;
        CMD_READ_TEMP_BASAL = 152;
        CMD_READ_STD_PROFILES
        CMD_READ_A_PROFILES = 147;
        CMD_READ_B_PROFILES = 148;
        CMD_READ_BG_ALARM_CLOCKS = 142;
        CMD_READ_BG_ALARM_ENABLE = 151;
        CMD_READ_BG_REMINDER_ENABLE = 144;
        CMD_READ_BG_TARGETS = 140;
        CMD_READ_BG_UNITS = 137;
        CMD_READ_BOLUS_WIZARD_SETUP_STATUS = 135;
        CMD_READ_CARB_RATIOS = 138;
        CMD_READ_CARB_UNITS = 136;
        CMD_READ_LOGIC_LINK_IDS = 149;
        CMD_READ_INSULIN_SENSITIVITIES = 139;
        CMD_READ_RESERVOIR_WARNING = 143;
        CMD_READ_PUMP_MODEL_NUMBER = 141;
        CMD_READ_LANGUAGE = 134;

      MMGuardian3/
        CMD_READ_SENSOR_SETTINGS = 207;
        CMD_READ_SENSOR_ALARM_SILENCE = 211;
        CMD_READ_SENSOR_DEMO_AND_GRAPH_TIMEOUT = 210
        CMD_READ_SENSOR_PREDICTIVE_ALERTS = 209;
        CMD_READ_SENSOR_RATE_OF_CHANGE_ALERTS = 212;

      MMX15/
        CMD_READ_SETTINGS = 192;
        CMD_READ_BG_TARGETS = 159;
        CMD_READ_CURRENT_HISTORY_PAGE_NUMBER = 157;
        CMD_READ_SAVED_SETTINGS_DATE = 193;
        CMD_READ_CONSTRAST = 195;
        CMD_READ_BOLUS_REMINDER_ENABLE = 197;
        CMD_READ_BOLUS_REMINDERS = 198;
        CMD_READ_FACTORY_PARAMETERS = 199;
        CMD_READ_CURRENT_PUMP_STATUS = 206;

      MMX22/ # production pump is a 522
        CMD_WRITE_GLUCOSE_HISTORY_TIMESTAMP = 40;
        CMD_READ_CURRENT_GLUCOSE_HISTORY_PAGE_NUMBER = 205;
        CMD_READ_GLUCOSE_HISTORY = 154;
        CMD_READ_CALIBRATION_FACTOR = 156;
        CMD_READ_ISIG_HISTORY = 155;
        CMD_READ_SENSOR_SETTINGS = 153;

      MMX23/
        CMD_READ_VCNTR_HISTORY = 213;
        CMD_READ_OTHER_DEVICES_IDS = 240;

