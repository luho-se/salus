import axios, {
	type AxiosInstance,
	type AxiosRequestConfig,
	type AxiosResponse,
	AxiosError,
} from "axios";

class ApiService {
	private api: AxiosInstance;

	constructor(baseURL: string) {
		this.api = axios.create({
			baseURL,
			headers: {
				"Content-Type": "application/json",
			},
			withCredentials: true, // Enable sending cookies with requests
		});

		// Handle request errors
		this.api.interceptors.request.use(undefined, (error) => {
			return Promise.reject(error);
		});
	}

	public get<T>(
		url: string,
		config?: AxiosRequestConfig,
	): Promise<AxiosResponse<T>> {
		return this.api.get<T>(url, config);
	}

	public post<T>(
		url: string,
		data?: unknown,
		config?: AxiosRequestConfig,
	): Promise<AxiosResponse<T>> {
		return this.api.post<T>(url, data, config);
	}

	public put<T>(
		url: string,
		data?: unknown,
		config?: AxiosRequestConfig,
	): Promise<AxiosResponse<T>> {
		return this.api.put<T>(url, data, config);
	}

	public patch<T>(
		url: string,
		data?: unknown,
		config?: AxiosRequestConfig,
	): Promise<AxiosResponse<T>> {
		return this.api.patch<T>(url, data, config);
	}

	public delete<T>(
		url: string,
		config?: AxiosRequestConfig,
	): Promise<AxiosResponse<T>> {
		return this.api.delete<T>(url, config);
	}

	public head<T>(
		url: string,
		config?: AxiosRequestConfig,
	): Promise<AxiosResponse<T>> {
		return this.api.head<T>(url, config);
	}

	public options<T>(
		url: string,
		config?: AxiosRequestConfig,
	): Promise<AxiosResponse<T>> {
		return this.api.options<T>(url, config);
	}
}

const apiService = new ApiService(import.meta.env.VITE_API_BASE_URL ?? "/api");

export default apiService;

export const getErrorMessage = (error: unknown, fallback: string): string => {
	if (error instanceof AxiosError) {
		return (
			(error.response?.data as { error?: string } | undefined)?.error ??
			fallback
		);
	}

	if (error instanceof Error) {
		return error.message;
	}

	return fallback;
};
