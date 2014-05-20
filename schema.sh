
CREATE AGGREGATE array_accum (anyelement)
(
  sfunc = array_append,
  stype = anyarray,
  initcond = '{}'
);

create table entities (entity_id text, freebase_id text, text text, raw_type text, type text) distributed by (entity_id);

create table relation_mention_features (doc_id text, mid1 text, mid2 text, word1 text, word2 text, type1 text, type2 text, features text[]) distributed by (doc_id);

create table relation_mentions (id bigint, doc_id text, mid1 text, mid2 text, word1 text, word2 text, rel text, is_correct bool) distributed by (doc_id);

create table el_cand_ext(doc_id text, mention_id text, entity text) distributed by (doc_id);

create table el_coref(doc_id text, mention_id text, mention_id text) distributed by (doc_id);

create table mentions(doc_id text, mention_id text, sentence_id text, word text, type text, start int, end int) distributed by (doc_id);

create table sentence (id bigint, doc_id text, text text, original_text text[], words text[], pos text[], ner text[], lemma text[], gender text[], true_case_text text[], timex_value text[], timex_type text[], character_offset_begin integer[], character_offset_end integer[], dep_graph text[], sentence_index integer, paragraph integer, sentence_token_offset_begin integer, constituency_parse text, sentence_id text) distributed by (doc_id);

