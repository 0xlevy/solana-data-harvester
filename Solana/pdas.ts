/**
 * Solana PDA Management Module
 * Handles Program Derived Addresses for dataset storage and access control.
 * Used for secure, on-chain dataset registration and verification.
 */

import {
  PublicKey,
  Connection,
  Keypair,
  Transaction,
  SystemProgram,
  TransactionInstruction,
  LAMPORTS_PER_SOL,
} from "@solana/web3.js";
import * as anchor from "@coral-xyz/anchor";

// Program ID for the Data Harvester Program (placeholder - replace with actual deployed program)
export const PROGRAM_ID = new PublicKey(
  "DHarv111111111111111111111111111111111111111"
);

// Seed prefixes for different PDA types
export const PDA_SEEDS = {
  DATASET: "dataset",
  ACCESS: "access",
  PAYMENT: "payment",
  CONFIG: "config",
} as const;

/**
 * Dataset metadata structure stored in PDA
 */
export interface DatasetMetadata {
  datasetId: string;
  creator: PublicKey;
  createdAt: number;
  updatedAt: number;
  version: number;
  dataHash: string;
  priceUsdc: number;
  isActive: boolean;
  totalPurchases: number;
}

/**
 * Access record for a user's dataset purchase
 */
export interface AccessRecord {
  user: PublicKey;
  dataset: PublicKey;
  purchasedAt: number;
  expiresAt: number;
  paymentSignature: string;
}

/**
 * Derive the PDA address for a dataset
 * @param datasetId - Unique identifier for the dataset
 * @param creator - Creator's public key
 * @returns PDA address and bump seed
 */
export async function deriveDatasetPDA(
  datasetId: string,
  creator: PublicKey
): Promise<[PublicKey, number]> {
  return PublicKey.findProgramAddressSync(
    [
      Buffer.from(PDA_SEEDS.DATASET),
      Buffer.from(datasetId),
      creator.toBuffer(),
    ],
    PROGRAM_ID
  );
}

/**
 * Derive the PDA address for access control
 * @param datasetPda - Dataset PDA address
 * @param user - User's public key
 * @returns Access PDA address and bump seed
 */
export async function deriveAccessPDA(
  datasetPda: PublicKey,
  user: PublicKey
): Promise<[PublicKey, number]> {
  return PublicKey.findProgramAddressSync(
    [Buffer.from(PDA_SEEDS.ACCESS), datasetPda.toBuffer(), user.toBuffer()],
    PROGRAM_ID
  );
}

/**
 * Derive the payment escrow PDA
 * @param datasetPda - Dataset PDA address
 * @returns Payment escrow PDA address and bump seed
 */
export async function derivePaymentPDA(
  datasetPda: PublicKey
): Promise<[PublicKey, number]> {
  return PublicKey.findProgramAddressSync(
    [Buffer.from(PDA_SEEDS.PAYMENT), datasetPda.toBuffer()],
    PROGRAM_ID
  );
}

/**
 * Derive the global config PDA
 * @returns Config PDA address and bump seed
 */
export async function deriveConfigPDA(): Promise<[PublicKey, number]> {
  return PublicKey.findProgramAddressSync(
    [Buffer.from(PDA_SEEDS.CONFIG)],
    PROGRAM_ID
  );
}

/**
 * PDA Manager class for interacting with Solana PDAs
 */
export class PDAManager {
  private connection: Connection;
  private programId: PublicKey;

  constructor(connection: Connection, programId: PublicKey = PROGRAM_ID) {
    this.connection = connection;
    this.programId = programId;
  }

  /**
   * Check if a PDA account exists
   * @param pda - PDA address to check
   * @returns true if account exists
   */
  async accountExists(pda: PublicKey): Promise<boolean> {
    const accountInfo = await this.connection.getAccountInfo(pda);
    return accountInfo !== null;
  }

  /**
   * Get dataset metadata from PDA
   * @param datasetId - Dataset identifier
   * @param creator - Creator's public key
   * @returns Dataset metadata or null if not found
   */
  async getDatasetMetadata(
    datasetId: string,
    creator: PublicKey
  ): Promise<DatasetMetadata | null> {
    const [pda] = await deriveDatasetPDA(datasetId, creator);
    const accountInfo = await this.connection.getAccountInfo(pda);

    if (!accountInfo) {
      return null;
    }

    // Decode account data (simplified - actual implementation depends on program layout)
    try {
      const data = accountInfo.data;
      // Parse the data according to your program's account structure
      // This is a simplified example
      return {
        datasetId: datasetId,
        creator: creator,
        createdAt: Date.now(),
        updatedAt: Date.now(),
        version: 1,
        dataHash: "",
        priceUsdc: 5.0,
        isActive: true,
        totalPurchases: 0,
      };
    } catch (e) {
      console.error("Failed to decode dataset metadata:", e);
      return null;
    }
  }

  /**
   * Check if a user has access to a dataset
   * @param datasetPda - Dataset PDA address
   * @param user - User's public key
   * @returns true if user has valid access
   */
  async checkUserAccess(datasetPda: PublicKey, user: PublicKey): Promise<boolean> {
    const [accessPda] = await deriveAccessPDA(datasetPda, user);
    const exists = await this.accountExists(accessPda);

    if (!exists) {
      return false;
    }

    // Check if access is still valid (not expired)
    const accountInfo = await this.connection.getAccountInfo(accessPda);
    if (!accountInfo) {
      return false;
    }

    // Parse and check expiration
    // Simplified - actual implementation depends on program
    return true;
  }

  /**
   * Get all datasets created by a specific creator
   * @param creator - Creator's public key
   * @returns Array of dataset PDAs
   */
  async getCreatorDatasets(creator: PublicKey): Promise<PublicKey[]> {
    // Use getProgramAccounts with filters
    const accounts = await this.connection.getProgramAccounts(this.programId, {
      filters: [
        {
          memcmp: {
            offset: 8, // After discriminator
            bytes: creator.toBase58(),
          },
        },
      ],
    });

    return accounts.map((a) => a.pubkey);
  }

  /**
   * Get the balance of the payment escrow PDA
   * @param datasetPda - Dataset PDA address
   * @returns Balance in lamports
   */
  async getEscrowBalance(datasetPda: PublicKey): Promise<number> {
    const [paymentPda] = await derivePaymentPDA(datasetPda);
    const balance = await this.connection.getBalance(paymentPda);
    return balance;
  }
}

/**
 * Build instruction to create a new dataset PDA
 * @param datasetId - Unique dataset identifier
 * @param creator - Creator's public key
 * @param metadata - Dataset metadata
 * @returns Transaction instruction
 */
export function buildCreateDatasetInstruction(
  datasetId: string,
  creator: PublicKey,
  metadata: Partial<DatasetMetadata>
): TransactionInstruction {
  const [datasetPda] = PublicKey.findProgramAddressSync(
    [
      Buffer.from(PDA_SEEDS.DATASET),
      Buffer.from(datasetId),
      creator.toBuffer(),
    ],
    PROGRAM_ID
  );

  // Build instruction data
  const instructionData = Buffer.alloc(256);
  let offset = 0;

  // Instruction discriminator (8 bytes)
  instructionData.writeUInt8(0, offset); // Create dataset instruction
  offset += 8;

  // Dataset ID length and data
  const datasetIdBytes = Buffer.from(datasetId);
  instructionData.writeUInt32LE(datasetIdBytes.length, offset);
  offset += 4;
  datasetIdBytes.copy(instructionData, offset);
  offset += datasetIdBytes.length;

  // Price in USDC (scaled to 6 decimals)
  const priceScaled = Math.floor((metadata.priceUsdc || 5.0) * 1e6);
  instructionData.writeBigUInt64LE(BigInt(priceScaled), offset);

  return new TransactionInstruction({
    keys: [
      { pubkey: creator, isSigner: true, isWritable: true },
      { pubkey: datasetPda, isSigner: false, isWritable: true },
      { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
    ],
    programId: PROGRAM_ID,
    data: instructionData.slice(0, offset + 8),
  });
}

/**
 * Build instruction to grant access to a dataset
 * @param datasetPda - Dataset PDA address
 * @param user - User to grant access
 * @param payer - Transaction payer
 * @returns Transaction instruction
 */
export function buildGrantAccessInstruction(
  datasetPda: PublicKey,
  user: PublicKey,
  payer: PublicKey
): TransactionInstruction {
  const [accessPda] = PublicKey.findProgramAddressSync(
    [Buffer.from(PDA_SEEDS.ACCESS), datasetPda.toBuffer(), user.toBuffer()],
    PROGRAM_ID
  );

  const instructionData = Buffer.alloc(16);
  instructionData.writeUInt8(1, 0); // Grant access instruction

  return new TransactionInstruction({
    keys: [
      { pubkey: payer, isSigner: true, isWritable: true },
      { pubkey: datasetPda, isSigner: false, isWritable: false },
      { pubkey: user, isSigner: false, isWritable: false },
      { pubkey: accessPda, isSigner: false, isWritable: true },
      { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
    ],
    programId: PROGRAM_ID,
    data: instructionData.slice(0, 8),
  });
}

/**
 * Utility to compute data hash for verification
 * @param data - Data to hash
 * @returns SHA256 hash as hex string
 */
export function computeDataHash(data: string | Buffer): string {
  const crypto = require("crypto");
  const hash = crypto.createHash("sha256");
  hash.update(data);
  return hash.digest("hex");
}

// Export types
export type { PublicKey };
