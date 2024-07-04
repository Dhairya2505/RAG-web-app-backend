import { Router } from "express";
import axios from 'axios';
export const getSolution = Router();
getSolution.post('/', async (req, res) => {
    const query = req.body.query;
    const response = await axios.post('http://localhost:5000/api/execute', {
        query
    });
    const answer = response.data.answer;
    res.json({
        msg: answer,
        status: 200
    });
});
