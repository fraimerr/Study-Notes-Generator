import { Hono } from "hono";
import generateRoute from "./routes/generate";

const app = new Hono().basePath("/api");

app.get("/", (c) => c.text("Hello World!"));

app.route("/generate", generateRoute);

export default app;
