import axios from 'axios';

const API_BASE_URL = '/api';

export const fetchSystemState = async () => {
  const res = await axios.get(`${API_BASE_URL}/state`);
  return res.data;
};

export const analyzeSituation = async (location, situation) => {
  const res = await axios.post(`${API_BASE_URL}/analyze`, { location, situation });
  return res.data;
};

export const sendChatMessage = async (message) => {
  const res = await axios.post(`${API_BASE_URL}/chat`, { message });
  return res.data;
};

export const triggerPlan = async () => {
  const res = await axios.post(`${API_BASE_URL}/plan`);
  return res.data;
};

export const triggerReplan = async () => {
  const res = await axios.post(`${API_BASE_URL}/replan`);
  return res.data;
};

export const addPresetZoneD = async () => {
  const res = await axios.post(`${API_BASE_URL}/zones/preset-d`);
  return res.data;
};

export const updateResources = async (resources) => {
  const res = await axios.post(`${API_BASE_URL}/resources`, resources);
  return res.data;
};

export const deleteZone = async (zoneId) => {
  const res = await axios.delete(`${API_BASE_URL}/zones/${zoneId}`);
  return res.data;
};

export const resetSystem = async () => {
  const res = await axios.post(`${API_BASE_URL}/reset`);
  return res.data;
};
