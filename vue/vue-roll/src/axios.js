import axios from "axios";

export const domainAddress = "http://127.0.0.1:5000";
export const baseApiURL= domainAddress + "/"

export const api =axios.create({
    baseURL: baseApiURL,
});
export default api;