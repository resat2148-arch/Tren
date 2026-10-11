import type {FilmEpisode} from './types';
import day01 from '../episodes/day-01.json';

// Neue Folge: Drehbuch unter episodes/ anlegen und hier eine Zeile ergänzen.
export const EPISODES: {id: string; data: FilmEpisode}[] = [{id: 'day-01', data: day01 as unknown as FilmEpisode}];
