--
-- This file defines the needed database tables.
--

-- replacement for PSQL's buggy array_agg()
DROP AGGREGATE IF EXISTS array_accum(anyelement);
CREATE AGGREGATE array_accum(anyelement)
(
  sfunc = array_append,
  stype = anyarray,
  initcond = '{}'
);

-- NOTE: DISTRIBUTED BY only supported in Greenplum; edit this file appropriately depending
-- on your database system

-- entity mentions
DROP TABLE IF EXISTS mentions CASCADE;
CREATE TABLE mentions (
	doc_id text,
	mention_id text,
	sentence_id text,
	word text,
	type text,
	start int,
	\"end\" int -- need to quote end, otherwise syntax error
) DISTRIBUTED BY (doc_id);


-- relation mentions
DROP TABLE IF EXISTS relation_mentions CASCADE;
CREATE TABLE relation_mentions (
	id bigint,
	doc_id text,
	mid1 text,
	mid2 text,
	word1 text,
	word2 text,
	rel text,
	is_correct boolean
) DISTRIBUTED BY (doc_id);


-- features for a given relation mention
-- (currently: word sequence, dependency path, presence of marriage keywords)
DROP TABLE IF EXISTS relation_mention_features CASCADE;
CREATE TABLE relation_mention_features (
	doc_id text,
	mid1 text,
	mid2 text,
	word1 text,
	word2 text,
	type1 text,
	type2 text,
	features text[]
) DISTRIBUTED BY (doc_id);
