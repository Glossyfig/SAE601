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
  url_source varchar NULL,
  categorie varchar NULL,
  name varchar NULL,
  image_url varchar NULL,
  set_number_id varchar NULL,
  card_number int NULL,
  artist varchar NULL,
  stage_evolution varchar NULL,
  pre_evolution varchar NULL,
  type_ varchar NULL,
  heal_points int NULL,
  weakness varchar NULL,
  retreat int NULL,
  attack_1_name varchar NULL,
  attack_1_cost varchar NULL,
  attack_1_damage varchar NULL,
  attack_2_name varchar NULL,
  attack_2_cost varchar NULL,
  attack_2_damage varchar NULL
);

DROP TABLE IF EXISTS public.wrk_tournaments_win;
CREATE TABLE public.wrk_tournaments_win (
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
