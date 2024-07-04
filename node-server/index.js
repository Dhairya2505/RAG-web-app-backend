import express from 'express';
import { getSolution } from './routes/getSolution.js';
const app = express();
app.use(express.json());
app.use('/getSolution', getSolution);
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on 'http://localhost:${PORT}'`);
});
