// output of db.contents.getIndexes() from PROD
var all_indexes = [
    {
        "v" : 1,
        "key" : {
            "_id" : 1
        },
        "ns" : "comments-prod.contents",
        "name" : "_id_"
    },
    {
        "v" : 1,
        "key" : {
            "parent_id" : 1
        },
        "ns" : "comments-prod.contents",
        "background" : true,
        "name" : "parent_id_1"
    },
    {
        "v" : 1,
        "key" : {
            "parent_ids" : 1
        },
        "ns" : "comments-prod.contents",
        "name" : "parent_ids_1"
    },
    {
        "v" : 1,
        "key" : {
            "tags_array" : 1
        },
        "ns" : "comments-prod.contents",
        "background" : true,
        "name" : "tags_array_1"
    },
    {
        "v" : 1,
        "key" : {
            "votes.up" : 1,
            "_type" : 1
        },
        "ns" : "comments-prod.contents",
        "name" : "votes.up_1__type_1",
        "background" : true
    },
    {
        "v" : 1,
        "key" : {
            "votes.down" : 1,
            "_type" : 1
        },
        "ns" : "comments-prod.contents",
        "name" : "votes.down_1__type_1",
        "background" : true
    },
    {
        "v" : 1,
        "key" : {
            "commentable_id" : 1,
            "created_at" : -1
        },
        "ns" : "comments-prod.contents",
        "name" : "commentable_id_1_created_at_-1",
        "background" : true
    },
    {
        "v" : 1,
        "key" : {
            "course_id" : 1,
            "_type" : 1,
            "created_at" : -1
        },
        "ns" : "comments-prod.contents",
        "name" : "course_id_1__type_1_created_at_-1",
        "background" : true
    },
    {
        "v" : 1,
        "key" : {
            "_type" : 1,
            "comment_thread_id" : 1,
            "author_id" : 1,
            "updated_at" : 1
        },
        "ns" : "comments-prod.contents",
        "name" : "_type_1_comment_thread_id_1_author_id_1_updated_at_1",
        "background" : true
    },
    {
        "v" : 1,
        "key" : {
            "comment_thread_id" : 1,
            "sk" : 1
        },
        "ns" : "comments-prod.contents",
        "name" : "comment_thread_id_1_sk_1",
        "background" : true,
        "sparse" : true
    },
    {
        "v" : 1,
        "key" : {
            "comment_thread_id" : 1,
            "endorsed" : 1
        },
        "ns" : "comments-prod.contents",
        "name" : "comment_thread_id_1_endorsed_1",
        "background" : true,
        "sparse" : true
    },
    {
        "v" : 1,
        "key" : {
            "_type" : 1,
            "course_id" : 1,
            "pinned" : -1,
            "created_at" : -1
        },
        "ns" : "comments-prod.contents",
        "name" : "_type_1_course_id_1_pinned_-1_created_at_-1",
        "background" : true
    },
    {
        "v" : 1,
        "key" : {
            "_type" : 1,
            "course_id" : 1,
            "pinned" : -1,
            "comment_count" : -1,
            "created_at" : -1
        },
        "ns" : "comments-prod.contents",
        "name" : "_type_1_course_id_1_pinned_-1_comment_count_-1_created_at_-1",
        "background" : true
    },
    {
        "v" : 1,
        "key" : {
            "_type" : 1,
            "course_id" : 1,
            "pinned" : -1,
            "votes.point" : -1,
            "created_at" : -1
        },
        "ns" : "comments-prod.contents",
        "name" : "_type_1_course_id_1_pinned_-1_votes.point_-1_created_at_-1",
        "background" : true
    },
    {
        "v" : 1,
        "key" : {
            "commentable_id" : 1
        },
        "ns" : "comments-prod.contents",
        "name" : "commentable_id_1",
        "sparse" : true,
        "background" : true
    },
    {
        "v" : 1,
        "key" : {
            "_type" : 1,
            "course_id" : 1,
            "context" : 1,
            "pinned" : -1,
            "created_at" : -1
        },
        "name" : "_type_1_course_id_1_context_1_pinned_-1_created_at_-1",
        "ns" : "comments-prod.contents",
        "background" : true
    },
    {
        "v" : 1,
        "key" : {
            "_type" : 1,
            "context" : 1
        },
        "name" : "_type_1_context_1",
        "ns" : "comments-prod.contents",
        "background" : true
    },
    {
        "v" : 1,
        "key" : {
            "_type" : -1,
            "course_id" : 1,
            "context" : 1,
            "pinned" : -1,
            "last_activity_at" : -1,
            "created_at" : -1
        },
        "name" : "_type_-1_course_id_1_context_1_pinned_-1_last_activity_at_-1_created_at_-1",
        "ns" : "comments-prod.contents",
        "background" : true
    },
    {
        "v" : 1,
        "key" : {
            "_type" : -1,
            "course_id" : 1,
            "commentable_id" : 1,
            "context" : 1,
            "pinned" : -1,
            "created_at" : -1
        },
        "name" : "_type_-1_course_id_1_commentable_id_1_context_1_pinned_-1_created_at_-1",
        "ns" : "comments-prod.contents",
        "background" : true
    },
    {
        "v" : 1,
        "key" : {
            "_type" : -1,
            "course_id" : 1,
            "endorsed" : -1,
            "pinned" : -1,
            "last_activity_at" : -1,
            "created_at" : -1
        },
        "name" : "_type_-1_course_id_1_endorsed_-1_pinned_-1_last_activity_at_-1_created_at_-1",
        "ns" : "comments-prod.contents",
        "background" : true
    },
    {
        "v" : 1,
        "key" : {
            "_type" : -1,
            "course_id" : 1,
            "endorsed" : -1,
            "pinned" : -1,
            "votes.point" : -1,
            "created_at" : -1
        },
        "name" : "_type_-1_course_id_1_endorsed_-1_pinned_-1_votes.point_-1_created_at_-1",
        "ns" : "comments-prod.contents",
        "background" : true
    },
    {
        "v" : 1,
        "key" : {
            "_type" : -1,
            "course_id" : 1,
            "endorsed" : -1,
            "pinned" : -1,
            "comment_count" : -1,
            "created_at" : -1
        },
        "name" : "_type_-1_course_id_1_endorsed_-1_pinned_-1_comment_count_-1_created_at_-1",
        "ns" : "comments-prod.contents",
        "background" : true
    },
    {
        "v" : 1,
        "key" : {
            "author_id" : 1,
            "course_id" : 1
        },
        "name" : "author_id_1_course_id_1",
        "ns" : "comments-prod.contents",
        "background" : true
    }
];

print('Getting list of indexes...');
var current_indexes = db.contents.getIndexes();

print('Current list of indexes:');
var list_of_current_index_names = [];
for (index = 0; index < current_indexes.length; index++) {
    print(current_indexes[index].name)
}

print('Ensuring indexes...');
var index,
    options;
for (index = 0; index < all_indexes.length; index++) {
    options = {
        background: (all_indexes[index].background === true),
        sparse: (all_indexes[index].sparse === true)
    }
    print('Ensuring ' + all_indexes[index].name);
    db.contents.ensureIndex(all_indexes[index].key, options);
}
