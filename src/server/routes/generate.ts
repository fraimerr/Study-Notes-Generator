import { Hono } from "hono";

const generateRoute = new Hono();

generateRoute.get("/", (c) => {
  return c.json({
    message: "response",
  });
});

export default generateRoute;