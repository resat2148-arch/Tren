import type {Episode} from './types';
import day01 from '../episodes/day-01.json';

// Neue Folge: JSON unter episodes/ anlegen und hier eine Zeile ergänzen.
export const EPISODES: {id: string; data: Episode}[] = [{id: 'day-01', data: day01 as unknown as Episode}];
