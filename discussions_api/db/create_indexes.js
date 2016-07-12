// output of db.contents.getIndexes() from PROD
var contentsIndexes = [
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


// output of db.subscriptions.getIndexes() from PROD
var subscriptionsIndexes = [
    {
        "v" : 1,
        "key" : {
            "_id" : 1
        },
        "ns" : "comments-prod.subscriptions",
        "name" : "_id_"
    },
    {
        "v" : 1,
        "key" : {
            "subscriber_id" : 1,
            "source_id" : 1,
            "source_type" : 1
        },
        "ns" : "comments-prod.subscriptions",
        "name" : "subscriber_id_1_source_id_1_source_type_1"
    },
    {
        "v" : 1,
        "key" : {
            "subscriber_id" : 1,
            "source_type" : 1
        },
        "ns" : "comments-prod.subscriptions",
        "name" : "subscriber_id_1_source_type_1"
    },
    {
        "v" : 1,
        "key" : {
            "subscriber_id" : 1
        },
        "ns" : "comments-prod.subscriptions",
        "name" : "subscriber_id_1"
    },
    {
        "v" : 1,
        "key" : {
            "source_id" : 1,
            "source_type" : 1
        },
        "ns" : "comments-prod.subscriptions",
        "name" : "source_id_1_source_type_1",
        "background" : true,
        "safe" : true
    }
]


// output of db.users.getIndexes() from PROD
var usersIndexes = [
    {
        "v" : 1,
        "key" : {
            "_id" : 1
        },
        "ns" : "comments-prod.users",
        "name" : "_id_"
    },
    {
        "v" : 1,
        "key" : {
            "external_id" : 1
        },
        "unique" : true,
        "ns" : "comments-prod.users",
        "name" : "external_id_1",
        "background" : true
    },
    {
        "v" : 1,
        "key" : {
            "username" : 1
        },
        "ns" : "comments-prod.users",
        "name" : "username_1",
        "background" : true
    },
    {
        "v" : 1,
        "key" : {
            "email" : 1
        },
        "ns" : "comments-prod.users",
        "name" : "email_1",
        "background" : true
    },
    {
        "v" : 1,
        "key" : {
            "external_id" : 1,
            "_id" : 1
        },
        "name" : "external_id_1__id_1",
        "background" : true,
        "ns" : "comments-prod.users"
    }
]


updateIndexes = function (collectionName, collectionIndexes) {
    print('Getting list of indexes for ' + collectionName + '...');
    var current_indexes = db[collectionName].getIndexes();

    print('Current list of indexes for ' + collectionName + ':');
    for (index = 0; index < current_indexes.length; index++) {
        print(current_indexes[index].name);
    }

    print('Dropping existing indexes...');
    db[collectionName].dropIndexes();

    print('Ensuring indexes for ' + collectionName + '...');
    var index,
        options;
    for (index = 0; index < collectionIndexes.length; index++) {
        options = {
            background: (collectionIndexes[index].background === true),
            sparse: (collectionIndexes[index].sparse === true)
        };
        print('Ensuring ' + collectionIndexes[index].name);
        db[collectionName].ensureIndex(collectionIndexes[index].key, options);
    }
};

updateIndexes('contents', contentsIndexes);
updateIndexes('subscriptions', subscriptionsIndexes);
updateIndexes('users', usersIndexes);
