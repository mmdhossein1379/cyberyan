from __future__ import annotations

from elasticsearch import AsyncElasticsearch

from app.core.config import settings


PROFILE_INDEX_DEFINITION = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "analysis": {
            "normalizer": {
                "lowercase_normalizer": {
                    "type": "custom",
                    "filter": [
                        "lowercase",
                    ],
                },
            },

            "filter": {
                "autocomplete_filter": {
                    "type": "edge_ngram",
                    "min_gram": 1,
                    "max_gram": 30,
                },
            },

            "analyzer": {
                "autocomplete_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "autocomplete_filter",
                    ],
                },


                "autocomplete_search_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                    ],
                },
            },
        },
    },

    "mappings": {
        "dynamic": "strict",

        "properties": {

            "id": {
                "type": "integer",
            },

            "full_name": {
                "type": "text",

                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "normalizer": "lowercase_normalizer",
                    },

                    "autocomplete": {
                        "type": "text",
                        "analyzer": "autocomplete_analyzer",
                        "search_analyzer": "autocomplete_search_analyzer",
                    },
                },
            },


            "linkedin_url": {
                "type": "keyword",
                "index": False,
            },


            "industry": {
                "type": "text",

                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "normalizer": "lowercase_normalizer",
                    },

                    "autocomplete": {
                        "type": "text",
                        "analyzer": "autocomplete_analyzer",
                        "search_analyzer": "autocomplete_search_analyzer",
                    },
                },
            },


            "job_title": {
                "type": "text",

                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "normalizer": "lowercase_normalizer",
                    },


                    "autocomplete": {
                        "type": "text",
                        "analyzer": "autocomplete_analyzer",
                        "search_analyzer": "autocomplete_search_analyzer",
                    },
                },
            },


            "job_company_name": {
                "type": "text",

                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "normalizer": "lowercase_normalizer",
                    },

                    "autocomplete": {
                        "type": "text",
                        "analyzer": "autocomplete_analyzer",
                        "search_analyzer": "autocomplete_search_analyzer",
                    },
                },
            },

            "location_name": {
                "type": "text",

                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "normalizer": "lowercase_normalizer",
                    },

                    "autocomplete": {
                        "type": "text",
                        "analyzer": "autocomplete_analyzer",
                        "search_analyzer": "autocomplete_search_analyzer",
                    },
                },
            },


            "summary": {
                "type": "text",
            },

            "skills": {
                "type": "text",

                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "normalizer": "lowercase_normalizer",
                    },

                    "autocomplete": {
                        "type": "text",
                        "analyzer": "autocomplete_analyzer",
                        "search_analyzer": "autocomplete_search_analyzer",
                    },
                },
            },

            "education": {
                "type": "object",
                "enabled": False,
            },


            "experience": {
                "type": "object",
                "enabled": False,
            },


            "search_text": {
                "type": "text",
            },
        },
    },
}


async def recreate_profile_index(
    client: AsyncElasticsearch,
) -> None:
    index_name = settings.elasticsearch_index

    exists = await client.indices.exists(
        index=index_name,
    )

    if exists:
        print(
            f"Deleting Elasticsearch index "
            f"'{index_name}'..."
        )

        await client.indices.delete(
            index=index_name,
        )

    print(
        f"Creating Elasticsearch index "
        f"'{index_name}'..."
    )

    await client.indices.create(
        index=index_name,
        settings=PROFILE_INDEX_DEFINITION["settings"],
        mappings=PROFILE_INDEX_DEFINITION["mappings"],
    )

    print(
        f"Elasticsearch index "
        f"'{index_name}' created."
    )