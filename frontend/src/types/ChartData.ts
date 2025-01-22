export interface ChartData {
    labels: string[]; 
    datasets: {
      label: string; 
      data: number[];
      yAxisID?: string;
      borderColor: string;
      backgroundColor?: string;
      fill?: boolean;
      tension?: number;
      pointRadius?: number[];
      pointBackgroundColor?: string[];
    }[];
  }
