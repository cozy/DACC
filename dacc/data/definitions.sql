insert into measure_definition(id, name, org, created_by, execution_frequency, group1_key, group2_key) values(1, 'session-duration', 'grandlyon', 'ecolyo', 'day', 'number_pages', 'session_type');
insert into measure_definition(id, name, org, created_by, aggregation_period, execution_frequency, group1_key) values(2, 'connection-count-daily', 'grandlyon', 'ecolyo', 'day', 'day', 'device');
insert into measure_definition(id, name, org, created_by, aggregation_period, execution_frequency, group1_key, group2_key, group3_key) values(3, 'navigation-action-daily', 'grandlyon', 'ecolyo', 'day', 'day', 'page', 'feature', 'params');
insert into measure_definition(id, name, org, created_by, aggregation_period, execution_frequency, group1_key, group2_key, group3_key) values(4, 'konnector-event-daily', 'grandlyon', 'ecolyo', 'day', 'day', 'slug', 'event_type', 'status');
insert into measure_definition(id, name, org, created_by, execution_frequency, group1_key, group2_key, group3_key) values(5, 'event-duration', 'grandlyon', 'ecolyo', 'day', 'start_event', 'end_event', 'params');
insert into measure_definition(id, name, org, created_by, aggregation_period, execution_frequency, group1_key) values(6, 'challenge-launch-daily', 'grandlyon', 'ecolyo', 'day', 'day', 'challenge_id');
insert into measure_definition(id, name, org, created_by, execution_frequency, group1_key, group2_key) values(7, 'quiz-stars', 'grandlyon', 'ecolyo', 'day', 'challenge_id', 'quiz_id');
insert into measure_definition(id, name, org, created_by, execution_frequency, group1_key, group2_key) values(8, 'duel-launch', 'grandlyon', 'ecolyo', 'day', 'challenge_id', 'duel_id');
insert into measure_definition(id, name, org, created_by, execution_frequency, group1_key, group2_key) values(9, 'duel-status', 'grandlyon', 'ecolyo', 'day', 'challenge_id', 'status');