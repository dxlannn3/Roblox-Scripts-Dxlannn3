const http = require("http");

// Servidor con ruta /ping para mantener el servicio activo (Cron-job.org)
const server = http.createServer((req, res) => {
  if (req.url === "/ping") {
    res.writeHead(200, { "Content-Type": "text/plain" });
    res.end("pong");
  }
});

const io = require("socket.io")(server, {
  cors: { origin: "*" }
});

const PORT = process.env.PORT || 3000;
const users = {}; // RAM pura: ID -> socketId

io.on("connection", (socket) => {
  console.log("Conexión detectada:", socket.id);

  // Registrar el ID de Voxid
  socket.on("register", (voxidId) => {
    users[voxidId] = socket.id;
    console.log(`ID Registrado: ${voxidId}`);
  });

  // Enviar mensaje directo (Relé Transparente)
  socket.on("send_message", (data) => {
    console.log('Mensaje Encifrado Enviado');
    const targetSocketId = users[data.to];
    if (targetSocketId) {
      io.to(targetSocketId).emit("receive_message", data);
    }
  });

  socket.on("disconnect", () => {
    for (let id in users) {
      if (users[id] === socket.id) delete users[id];
    }
  });
});

server.listen(PORT, () => {
  console.log(`Servidor Voxid Ghost corriendo en el puerto ${PORT}...`);
});
