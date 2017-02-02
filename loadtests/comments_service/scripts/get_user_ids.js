rs.slaveOk();

var num_records = 1000;
var user_ids = [];
var users = db.users.find();
var i;
for (i = 0; i < num_records && users.hasNext(); i++) {
    user_ids.push(users.next().external_id);
}
printjson(user_ids);
