// Extracted from manuscript/book1-traditional/12-nosql-databases.md §12.5.3 (listing 2). Edit the manuscript, not this file.
// Orders of one customer, newest first, above a value threshold
db.orders.createIndex({ customer_id: 1, placed_at: -1, total: 1 });   // E, S, R

db.orders.find({ customer_id: "c42", total: { $gte: 50 } })
         .sort({ placed_at: -1 })
         .limit(20);

// A transaction across two documents (replica set or sharded cluster)
const session = db.getMongo().startSession();
session.withTransaction(() => {
  const s = session.getDatabase("shop");
  s.inventory.updateOne({ sku: "SKU-1", qty: { $gte: 2 } }, { $inc: { qty: -2 } });
  s.orders.insertOne({ _id: "o902", customer_id: "c42", items: [{ sku: "SKU-1", qty: 2 }] });
}, { writeConcern: { w: "majority" } });
