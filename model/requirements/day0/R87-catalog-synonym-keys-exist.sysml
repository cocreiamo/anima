package R87 {
    private import Anima::*;

    requirement <'R87'> catalogSynonymKeysExist {
        doc /* Every key of the synonyms file of the catalog shall name something that exists. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy catalogSynonymKeysExist by toolchain;

    verification def test_R87_catalog_synonym_keys_exist {
        subject tools : Toolchain;
        objective { verify catalogSynonymKeysExist; }
    }
}
