export interface ApiResponse<T> {

    success: boolean;

    message: string;

    data: T;

}

export interface Pagination {

    page: number;

    page_size: number;

    total: number;

    total_pages: number;

}

export interface PaginatedResponse<T> {

    success: boolean;

    message: string;

    data: T[];

    pagination: Pagination;

}