export interface Project {
	project_id: number;
	project_title: string;
}

export interface Code {
	code_id: number;
	term: string;
	description: string;
	type_id: number;
	code_type?: {
		type_id: number;
		type_name: string;
	};
	reference?: string;
	coordinates?: string;
}

export interface CodeType {
	type_id: number;
	type_name: string;
}

export interface Annotation {
	annotation_id: number;
	element_id: number;
	code?: {
		code_id: number;
		term: string;
	};
}

export interface Element {
    element_id: number;
    element_text: string;
    segment?: {
        segment_id: number;
        segment_title?: string; 
        series?: {
            series_id: number;
            series_title?: string;
        };
    };
    annotations: Array<{
        annotation_id: number;
        code?: {
            code_id: number;
            term: string;
        };
    }>;
}

export interface Series {
	series_id: number;
	series_title: string;
}

export interface Series {
	segment_id: number;
	segment_title: string;
}
