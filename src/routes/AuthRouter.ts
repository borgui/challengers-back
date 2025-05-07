import { Router } from "express";
import LoginController from "../controllers/login-controller";

const authRouter = Router();

authRouter.post('/login', LoginController.perform);

export default authRouter