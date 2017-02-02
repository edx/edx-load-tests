rs.slaveOk();

var num_records = 1000;
var commentable_ids = [];
var threads = db.contents.find({ _type: 'CommentThread' });
var i;
for (i = 0; i < num_records && threads.hasNext(); i++) {
    commentable_ids.push(threads.next().commentable_id);
}
printjson(commentable_ids);
