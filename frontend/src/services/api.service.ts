import axios, {
	type AxiosInstance,
	type AxiosRequestConfig,
	type AxiosResponse,
	AxiosError,
} from "axios";

function toCamel(str: string): string {
	return str.replace(/_([a-z])/g, (_, c) => c.toUpperCase());
}

function toSnake(str: string): string {
	return str.replace(/([A-Z])/g, (c) => `_${c.toLowerCase()}`);
}

function transformKeys(obj: unknown, transform: (key: string) => string): unknown {
	if (Array.isArray(obj)) return obj.map((item) => transformKeys(item, transform));
	if (obj !== null && typeof obj === "object") {
		return Object.fromEntries(
			Object.entries(obj as Record<string, unknown>).map(([k, v]) => [
				transform(k),
				transformKeys(v, transform),
			]),
		);
	}
	return obj;
}

class ApiService {
	private api: AxiosInstance;

	constructor(baseURL: string) {
		this.api = axios.create({
			baseURL,
			headers: {
				"Content-Type": "application/json",
			},
			withCredentials: true,
		});

		this.api.interceptors.request.use((config) => {
			if (config.data) {
				config.data = transformKeys(config.data, toSnake);
			}
			return config;
		});

		this.api.interceptors.response.use(
			(response) => {
				if (response.data) {
					response.data = transformKeys(response.data, toCamel);
				}
				return response;
			},
			(error) => Promise.reject(error),
		);
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
