import { Router } from 'express';
import authRouter from './AuthRouter';


const router = Router();

router.all("/auth", authRouter)

export default router;
