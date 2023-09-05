'''

CREATE TABLE bms (
    Time TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,  -- Auto-filled timestamp
    PackCurrent0_1A NUMERIC ,
    PackInstantaneousVoltage0_1V NUMERIC ,
    PackStateOfCharge NUMERIC ,
    PackAmphours0_1Ahr NUMERIC ,
    PackHealth1 NUMERIC ,
    HighTemperatureC NUMERIC ,
    HighTempCellID NUMERIC ,
    LowTemperatureC NUMERIC ,
    LowTempCellID NUMERIC ,
    AverageTemperatureC NUMERIC ,
    InternalTemperatureC NUMERIC ,
    LowCellVoltage0_0001V NUMERIC ,
    LowCellVoltageID NUMERIC ,
    HighCellVoltage0_0001V NUMERIC ,
    HighCellVoltageID NUMERIC ,
    AverageCellVoltage0_0001V NUMERIC 
);

CREATE TABLE errorcodes (
    Time TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,  -- Auto-filled timestamp
    pedalsensor INTEGER,
    safetycircuit INTEGER,
    canfailed INTEGER,
    looptoolong INTEGER,
    errorimd INTEGER
);

CREATE TABLE data (
    Time TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,  -- Auto-filled timestamp
    speed NUMERIC
);

CREATE TABLE state (
    Time TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,  -- Auto-filled timestamp
    vcuState INTEGER
);

'''