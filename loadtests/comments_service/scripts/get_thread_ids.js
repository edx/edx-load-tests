rs.slaveOk();

var num_records = 1000;
var thread_ids = [];
var threads = db.contents.find({ _type: 'CommentThread' });
var i;
for (i = 0; i < num_records && threads.hasNext(); i++) {
    thread_ids.push(threads.next()._id.str);
}
printjson(thread_ids);
