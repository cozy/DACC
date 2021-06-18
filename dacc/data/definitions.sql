insert into measure_definition(id, name, org, access_app, access_public, created_by, execution_frequency, group1_key, group2_key, description) values(1, 'session-duration', 'grandlyon', false, false, 'ecolyo', 'day', 'number_pages', 'session_type', 'Durée d''une session utilisateur');
insert into measure_definition(id, name, org, access_app, access_public, created_by, aggregation_period, execution_frequency, group1_key, description) values(2, 'connection-count-daily', 'grandlyon', false, false, 'ecolyo', 'day', 'day', 'device', 'Nombre de connexions');
insert into measure_definition(id, name, org, access_app, access_public, created_by, aggregation_period, execution_frequency, group1_key, group2_key, group3_key, description) values(3, 'navigation-action-daily', 'grandlyon', false, false, 'ecolyo', 'day', 'day', 'page', 'feature', 'params', 'Actions de navigation');
insert into measure_definition(id, name, org, access_app, access_public, created_by, aggregation_period, execution_frequency, group1_key, group2_key, group3_key, description) values(4, 'konnector-event-daily', 'grandlyon', false, false, 'ecolyo', 'day', 'day', 'slug', 'event_type', 'status', 'Evènements de connecteur');
insert into measure_definition(id, name, org, access_app, access_public, created_by, execution_frequency, group1_key, group2_key, group3_key, description) values(5, 'event-duration', 'grandlyon', false, false, 'ecolyo', 'day', 'start_event', 'end_event', 'params', 'Durée entre évènements');
insert into measure_definition(id, name, org, access_app, access_public, created_by, aggregation_period, execution_frequency, group1_key, description) values(6, 'challenge-launch-daily', 'grandlyon', false, false, 'ecolyo', 'day', 'day', 'challenge_id', 'Nombre de défis lancés lors d''un challenge');
insert into measure_definition(id, name, org, access_app, access_public, created_by, execution_frequency, group1_key, group2_key, description) values(7, 'quiz-stars', 'grandlyon', false, false, 'ecolyo', 'day', 'challenge_id', 'quiz_id', 'Nombre d''étoiles obtenues lors d''un quiz');
insert into measure_definition(id, name, org, access_app, access_public, created_by, execution_frequency, group1_key, group2_key,description) values(8, 'duel-launch', 'grandlyon', false, false, 'ecolyo', 'day', 'challenge_id', 'duel_id', 'Lancement d''un duel');
insert into measure_definition(id, name, org, access_app, access_public, created_by, execution_frequency, group1_key, group2_key, description) values(9, 'duel-status', 'grandlyon', false, false, 'ecolyo', 'day', 'challenge_id', 'status', 'Succès ou échecs de duels');
