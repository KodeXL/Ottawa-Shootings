SELECT * from shootingsottawa;
UPDATE shootingsottawa SET `Reported Date` = REPLACE (`Reported Date` , '/', '-'); 
UPDATE shootingsottawa SET `Occurred Date` = REPLACE (`Occurred Date` , '/', '-'); 
UPDATE shootingsottawa SET `Reported Date` = STR_TO_DATE(`Reported Date`,'%c-%e-%Y %h:%i:%s %p');
UPDATE shootingsottawa SET `Occurred Date` = STR_TO_DATE(`Occurred Date`,'%c-%e-%Y %h:%i:%s %p');
ALTER TABLE shootingsottawa 
CHANGE `Reported Date` Reported_Date DATETIME,
CHANGE `Reported Hour` Reported_Hour TIME,
CHANGE `Reported Year` Reported_Year INT,
CHANGE `Occurred Date` Occurred_Date DATETIME,
CHANGE `Occurred Hour` Occurred_Hour TIME,
CHANGE `Occurred Year` Occurred_Year INT,
CHANGE `Time of Day` Time_of_Day TEXT,
CHANGE `Day of Week` Day_of_Week CHAR(1),
CHANGE `Census Tract` Census_Tract DOUBLE,
CHANGE `Level of Injury` Level_of_Injury VARCHAR(7);
UPDATE shootingsottawa SET Reported_Date = DATE(Reported_Date);
UPDATE shootingsottawa SET Occurred_Date = DATE(Occurred_Date);
ALTER TABLE shootingsottawa
MODIFY COLUMN Reported_Date DATE,
MODIFY COLUMN Occurred_Date DATE;
ALTER TABLE shootingsottawa DROP COLUMN OBJECTID;
ALTER TABLE shootingsottawa 
ADD COLUMN Reported_Month VARCHAR(10) after Reported_Date, 
ADD COLUMN Occurred_Month VARCHAR(10) after Occurred_Date;
UPDATE shootingsottawa SET Reported_Month = MONTHNAME(Reported_Date);
UPDATE shootingsottawa SET Occurred_Month = MONTHNAME(Occurred_Date);
ALTER TABLE shootingsottawa 
DROP COLUMN Reported_Date,
DROP COLUMN Reported_Year,
DROP COLUMN Reported_Hour,
DROP COLUMN Reported_Month,
DROP COLUMN Occurred_Hour,
DROP COLUMN Day_of_Week,
DROP COLUMN Sector,
DROP COLUMN Census_Tract;
ALTER TABLE shootingsottawa modify Ward VARCHAR(85);
CREATE VIEW LOI AS
SELECT * from shootingsottawa WHERE Level_of_Injury <> '';
SELECT * FROM loi;