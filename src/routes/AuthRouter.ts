import { Router } from "express";
import LoginController from "../controllers/LoginController";

const authRouter = Router();

authRouter.post('/login', LoginController.perform);

export default authRouter