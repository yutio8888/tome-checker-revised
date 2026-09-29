-- Reviewed production player tokens. List a body family here (e.g.
-- human_male=true) only after data/gfx/tokens/player-<family>.png has been
-- exported and reviewed. The runtime also checks that the file exists.
-- Empty: every player keeps native art.
--
-- players-v1: 13 of the 14 native body families from art/player-tokens-v1
-- (ImageGen batch, see art/player-tokens-v1/REVIEW.md). halfling_female is
-- withheld: both imagegen attempts failed provenance (codex returned no
-- image), budget exhausted; it keeps native art until a future batch.
return {
 revision='players-v1',
 families={
  human_male=true, human_female=true,
  elf_male=true, elf_female=true,
  dwarf_male=true, dwarf_female=true,
  halfling_male=true,
  ogre_male=true, ogre_female=true,
  yeek=true, ghoul=true, skeleton=true, runic_golem=true,
 },
}
