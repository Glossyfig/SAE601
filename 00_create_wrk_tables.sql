-- public.tournaments definition
DROP TABLE IF EXISTS public.wrk_tournaments;
CREATE TABLE public.wrk_tournaments (
  tournament_id varchar NULL,
  tournament_name varchar NULL,
  tournament_date timestamp NULL,
  tournament_organizer varchar NULL,
  tournament_format varchar NULL,
  tournament_nb_players int NULL
);

DROP TABLE IF EXISTS public.wrk_decklists;
CREATE TABLE public.wrk_decklists (
  tournament_id varchar NULL,
  player_id varchar NULL,
  card_type varchar NULL,
  card_name varchar NULL,
  card_url varchar NULL,
  card_count int NULL
);

ALTER TABLE wrk_tournaments
ADD COLUMN tournament_date_y INT,
ADD COLUMN tournament_date_m INT,
ADD COLUMN tournament_date_d INT;
UPDATE wrk_tournaments SET tournament_date_y = EXTRACT(YEAR FROM tournament_date)::INT;
UPDATE wrk_tournaments SET tournament_date_m = EXTRACT(Month FROM tournament_date)::INT;
UPDATE wrk_tournaments SET tournament_date_d = EXTRACT(DAY FROM tournament_date)::INT;

DROP TABLE IF EXISTS public.wrk_cards;
CREATE TABLE public.wrk_cards (
  url_source text NULL,
  categorie text NULL,
  name text NULL,
  image_url text NULL,
  set_number_id text NULL,
  card_number int NULL,
  artist text NULL,
  stage_evolution text NULL,
  pre_evolution text NULL,
  type_ text NULL,
  heal_points int NULL,
  weakness text NULL,
  retreat int NULL,
  attack_1_name text NULL,
  attack_1_cost text NULL,
  attack_1_damage text NULL,
  attack_2_name text NULL,
  attack_2_cost text NULL,
  attack_2_damage text NULL
);

DROP TABLE IF EXISTS public.wrk_tournaments_win;
CREATE TABLE public.wrk_tournaments (
  tournament_id varchar NULL,
  tournament_name varchar NULL,
  name varchar NULL,
  placing int NULL,
  victories int NULL,
  losses int NULL,
  draws int NULL,
  winrates decimal NULL,
  deck varchar NULL
);
