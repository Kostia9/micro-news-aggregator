// Safe to rerun when Docker volumes already contain an initialized replica set.

function waitForPrimary() {
  for (let attempt = 1; attempt <= 30; attempt++) {
    const status = rs.status();
    const primary = status.members.find((member) => member.stateStr === "PRIMARY");
    if (primary) {
      print(`Replica set primary is ${primary.name}`);
      return;
    }
    sleep(1000);
  }
  throw new Error("Replica set did not elect a primary in time");
}

try {
  const status = rs.status();
  if (status.ok === 1) {
    print("Replica set already initialized");
    waitForPrimary();
    quit(0);
  }
} catch (error) {
  if (error.codeName !== "NotYetInitialized") {
    throw error;
  }
}

rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "mongo1:27017", priority: 2 },
    { _id: 1, host: "mongo2:27017", priority: 1 },
    { _id: 2, host: "mongo3:27017", priority: 1 }
  ]
});

waitForPrimary();
