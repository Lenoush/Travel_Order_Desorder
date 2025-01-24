// types.ts

// Interface pour une réponse de route
export interface RouteResponse {
    responsesmodel: RouteItem[] | string[];
    text: string;
}
  
// Interface pour un élément de route
export interface RouteItem {
    label: string;
    word: string;
}

