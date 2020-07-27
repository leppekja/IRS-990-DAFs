DROP TABLE IF EXISTS grantees;
DROP TABLE IF EXISTS sponsors;

CREATE TABLE sponsors (
    id serial,
    ein char(9) NOT NULL,
    name varchar(100),
    address_line_1 varchar(60),
    city varchar(50),
    state_abbr char(2),
    zip char(5),
    location point,
    daf_held_cnt int,
    daf_contri_amt int,
    daf_grants_amt int,
    daf_eoy_amt int,
    disclosed_legal boolean,
    disclosed_prps boolean,
    other_act_held_cnt int,
    other_act_contri_amt int,
    other_act_grants_amt int,
    other_act_eoy_amt int,
    PRIMARY KEY (id),
);

CREATE TABLE grantees (
    id serial,
    business_name_line_1 varchar(100),
    business_name_line_2 varchar(50),
    address_line_1 varchar(60),
    address_line_2 varchar(60),
    city varchar(50),
    state_abbr char(2),
    zip char(5),
    location point,
    ein char(9) NOT NULL,
    irs_section_desc varchar(10),
    cash_grant_amt float,
    purpose_of_grant varchar(100),
    sponsor_ein char(9),
    grant_type varchar(50),
    PRIMARY KEY (id)
    FOREIGN KEY (sponsor_ein) REFERENCES sponsors
);