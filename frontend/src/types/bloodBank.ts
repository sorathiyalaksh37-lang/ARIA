import { GeoLocation } from './incident';

/**
 * Types for Blood Banks and Blood Inventory
 */

/**
 * Standard blood groups.
 */
export enum BloodType {
  A_POS = 'A+',
  A_NEG = 'A-',
  B_POS = 'B+',
  B_NEG = 'B-',
  AB_POS = 'AB+',
  AB_NEG = 'AB-',
  O_POS = 'O+',
  O_NEG = 'O-',
}

/**
 * Inventory records for blood types (in units).
 */
export type BloodInventory = Record<BloodType, number>;

/**
 * Core interface representing a blood bank facility.
 */
export interface BloodBank {
  id: string;
  name: string;
  address: string;
  location: GeoLocation;
  phone: string;
  inventory: BloodInventory;
  last_updated: string;
}
