import axios from 'axios';

const BASE_URL = 'http://localhost:8000';

export async function fetchCodes() {
    try {
        const response = await axios.get(`${BASE_URL}/codes/`);
        return response.data;
    } catch (error) {
        console.error('Error fetching codes:', error);
        throw error;
    }
}

export async function fetchCodeTypes() {
    try {
        const response = await axios.get(`${BASE_URL}/code_types/`);
        return response.data;
    } catch (error) {
        console.error('Error fetching code types:', error);
        throw error;
    }
}

export async function addCode(newCode) {
    try {
        const response = await axios.post(`${BASE_URL}/codes/`, newCode);
        return response.data;  // This should be the newly created code
    } catch (error) {
        console.error('Error adding code:', error);
        throw error;
    }
}

export async function updateCode(id, updatedCode) {
    try {
        const response = await axios.put(`${BASE_URL}/codes/${id}`, updatedCode);
        return response.data;
    } catch (error) {
        console.error('Error updating code:', error);
        throw error;
    }
}

export async function deleteCode(id) {
    try {
        await axios.delete(`${BASE_URL}/codes/${id}`);
    } catch (error) {
        console.error('Error deleting code:', error);
        throw error;
    }
}