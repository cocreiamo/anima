package R19 {
    private import Anima::*;

    requirement <'R19'> vectorSearchInEveryDatabase {
        doc /* Every database, including one created after first start,
             * shall offer vector similarity search without any
             * installation step. */
        subject vectors : VectorSearch;
    }

    satisfy vectorSearchInEveryDatabase by anima.engine.pgvector;

    verification def test_R19_vector_search_in_every_database {
        subject sys : System;
        objective { verify vectorSearchInEveryDatabase; }
    }
}
