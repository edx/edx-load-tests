rs.slaveOk();

var num_records = 1000;
var comment_ids = [];
var comments = db.contents.find({ _type: 'Comment' });
var i;
for (i = 0; i < num_records && comments.hasNext(); i++) {
    comment_ids.push(comments.next()._id.str);
}
printjson(comment_ids);
