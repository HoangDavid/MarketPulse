export interface MarketData{
    timestamp: string,
    price: number,
    fear_greed_score: number,
    correlation: number,
    sentiment: number,
    article_url: string,
    title: string,
    top_comment: string,
    positive_spike: boolean,
    negative_spike: boolean,
    action: string
}