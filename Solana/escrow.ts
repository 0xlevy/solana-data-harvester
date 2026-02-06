/**
 * Solana Escrow & Payment Module
 * Handles USDC payments for dataset access via AgentWallet integration.
 * Implements secure escrow pattern for trustless dataset monetization.
 */

import {
  PublicKey,
  Connection,
  Transaction,
  TransactionInstruction,
  SystemProgram,
  LAMPORTS_PER_SOL,
  Keypair,
  sendAndConfirmTransaction,
} from "@solana/web3.js";
import {
  TOKEN_PROGRAM_ID,
  ASSOCIATED_TOKEN_PROGRAM_ID,
  getAssociatedTokenAddress,
  createTransferInstruction,
  getAccount,
} from "@solana/spl-token";
import {
  PROGRAM_ID,
  deriveDatasetPDA,
  derivePaymentPDA,
  deriveAccessPDA,
  PDA_SEEDS,
} from "./pdas";

// USDC Mint on Solana Mainnet
export const USDC_MINT = new PublicKey(
  "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
);

// USDC has 6 decimals
export const USDC_DECIMALS = 6;

/**
 * Payment status enum
 */
export enum PaymentStatus {
  PENDING = "pending",
  COMPLETED = "completed",
  FAILED = "failed",
  REFUNDED = "refunded",
}

/**
 * Payment record structure
 */
export interface PaymentRecord {
  id: string;
  buyer: PublicKey;
  seller: PublicKey;
  datasetId: string;
  amountUsdc: number;
  status: PaymentStatus;
  signature: string | null;
  createdAt: number;
  completedAt: number | null;
}

/**
 * Escrow state structure
 */
export interface EscrowState {
  datasetPda: PublicKey;
  escrowPda: PublicKey;
  seller: PublicKey;
  totalDeposited: number;
  totalWithdrawn: number;
  isActive: boolean;
}

/**
 * EscrowManager handles all payment and escrow operations
 */
export class EscrowManager {
  private connection: Connection;
  private agentWalletKey: string;

  constructor(connection: Connection, agentWalletKey: string) {
    this.connection = connection;
    this.agentWalletKey = agentWalletKey;
  }

  /**
   * Get USDC token account for a wallet
   * @param owner - Wallet owner
   * @returns Associated token account address
   */
  async getUsdcTokenAccount(owner: PublicKey): Promise<PublicKey> {
    return getAssociatedTokenAddress(USDC_MINT, owner);
  }

  /**
   * Get USDC balance for a wallet
   * @param owner - Wallet owner
   * @returns Balance in USDC (decimal)
   */
  async getUsdcBalance(owner: PublicKey): Promise<number> {
    try {
      const tokenAccount = await this.getUsdcTokenAccount(owner);
      const account = await getAccount(this.connection, tokenAccount);
      return Number(account.amount) / Math.pow(10, USDC_DECIMALS);
    } catch (e) {
      console.error("Failed to get USDC balance:", e);
      return 0;
    }
  }

  /**
   * Create payment instruction for dataset purchase
   * @param buyer - Buyer's public key
   * @param seller - Seller's public key
   * @param amountUsdc - Amount in USDC
   * @returns Transaction instruction
   */
  async createPaymentInstruction(
    buyer: PublicKey,
    seller: PublicKey,
    amountUsdc: number
  ): Promise<TransactionInstruction> {
    const buyerTokenAccount = await this.getUsdcTokenAccount(buyer);
    const sellerTokenAccount = await this.getUsdcTokenAccount(seller);
    const amountScaled = BigInt(Math.floor(amountUsdc * Math.pow(10, USDC_DECIMALS)));

    return createTransferInstruction(
      buyerTokenAccount,
      sellerTokenAccount,
      buyer,
      amountScaled,
      [],
      TOKEN_PROGRAM_ID
    );
  }

  /**
   * Create escrow deposit instruction
   * Deposits USDC into the escrow PDA for later release
   * @param datasetPda - Dataset PDA
   * @param depositor - Depositor's public key
   * @param amountUsdc - Amount to deposit
   * @returns Transaction instruction
   */
  async createEscrowDepositInstruction(
    datasetPda: PublicKey,
    depositor: PublicKey,
    amountUsdc: number
  ): Promise<TransactionInstruction> {
    const [escrowPda] = await derivePaymentPDA(datasetPda);
    const depositorTokenAccount = await this.getUsdcTokenAccount(depositor);
    const escrowTokenAccount = await this.getUsdcTokenAccount(escrowPda);
    const amountScaled = BigInt(Math.floor(amountUsdc * Math.pow(10, USDC_DECIMALS)));

    // Build escrow deposit instruction
    const instructionData = Buffer.alloc(32);
    instructionData.writeUInt8(2, 0); // Escrow deposit instruction discriminator
    instructionData.writeBigUInt64LE(amountScaled, 8);

    return new TransactionInstruction({
      keys: [
        { pubkey: depositor, isSigner: true, isWritable: true },
        { pubkey: depositorTokenAccount, isSigner: false, isWritable: true },
        { pubkey: escrowPda, isSigner: false, isWritable: true },
        { pubkey: escrowTokenAccount, isSigner: false, isWritable: true },
        { pubkey: datasetPda, isSigner: false, isWritable: false },
        { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      ],
      programId: PROGRAM_ID,
      data: instructionData.slice(0, 16),
    });
  }

  /**
   * Create escrow release instruction
   * Releases escrowed USDC to the seller after access is granted
   * @param datasetPda - Dataset PDA
   * @param seller - Seller's public key
   * @param amountUsdc - Amount to release
   * @returns Transaction instruction
   */
  async createEscrowReleaseInstruction(
    datasetPda: PublicKey,
    seller: PublicKey,
    amountUsdc: number
  ): Promise<TransactionInstruction> {
    const [escrowPda] = await derivePaymentPDA(datasetPda);
    const escrowTokenAccount = await this.getUsdcTokenAccount(escrowPda);
    const sellerTokenAccount = await this.getUsdcTokenAccount(seller);
    const amountScaled = BigInt(Math.floor(amountUsdc * Math.pow(10, USDC_DECIMALS)));

    const instructionData = Buffer.alloc(32);
    instructionData.writeUInt8(3, 0); // Escrow release instruction discriminator
    instructionData.writeBigUInt64LE(amountScaled, 8);

    return new TransactionInstruction({
      keys: [
        { pubkey: seller, isSigner: true, isWritable: false },
        { pubkey: escrowPda, isSigner: false, isWritable: true },
        { pubkey: escrowTokenAccount, isSigner: false, isWritable: true },
        { pubkey: sellerTokenAccount, isSigner: false, isWritable: true },
        { pubkey: datasetPda, isSigner: false, isWritable: false },
        { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      ],
      programId: PROGRAM_ID,
      data: instructionData.slice(0, 16),
    });
  }

  /**
   * Process a complete dataset purchase
   * Handles payment, escrow, and access grant in a single transaction
   * @param buyer - Buyer's keypair
   * @param datasetId - Dataset identifier
   * @param seller - Seller's public key
   * @param priceUsdc - Price in USDC
   * @returns Payment record
   */
  async purchaseDataset(
    buyer: Keypair,
    datasetId: string,
    seller: PublicKey,
    priceUsdc: number
  ): Promise<PaymentRecord> {
    const paymentId = `pay_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    const record: PaymentRecord = {
      id: paymentId,
      buyer: buyer.publicKey,
      seller: seller,
      datasetId: datasetId,
      amountUsdc: priceUsdc,
      status: PaymentStatus.PENDING,
      signature: null,
      createdAt: Date.now(),
      completedAt: null,
    };

    try {
      // Check buyer balance
      const balance = await this.getUsdcBalance(buyer.publicKey);
      if (balance < priceUsdc) {
        throw new Error(`Insufficient USDC balance. Have: ${balance}, Need: ${priceUsdc}`);
      }

      // Derive PDAs
      const [datasetPda] = await deriveDatasetPDA(datasetId, seller);
      const [accessPda] = await deriveAccessPDA(datasetPda, buyer.publicKey);

      // Build transaction with multiple instructions
      const transaction = new Transaction();

      // 1. Payment instruction
      const paymentIx = await this.createPaymentInstruction(
        buyer.publicKey,
        seller,
        priceUsdc
      );
      transaction.add(paymentIx);

      // 2. Grant access instruction
      const grantAccessIx = this.buildGrantAccessInstruction(
        datasetPda,
        buyer.publicKey,
        seller
      );
      transaction.add(grantAccessIx);

      // Send and confirm transaction
      const signature = await sendAndConfirmTransaction(
        this.connection,
        transaction,
        [buyer],
        { commitment: "confirmed" }
      );

      record.signature = signature;
      record.status = PaymentStatus.COMPLETED;
      record.completedAt = Date.now();

      console.log(`Payment completed: ${signature}`);
      return record;
    } catch (e) {
      record.status = PaymentStatus.FAILED;
      console.error("Payment failed:", e);
      throw e;
    }
  }

  /**
   * Build grant access instruction
   * @param datasetPda - Dataset PDA
   * @param user - User to grant access
   * @param authority - Authority (seller)
   * @returns Transaction instruction
   */
  private buildGrantAccessInstruction(
    datasetPda: PublicKey,
    user: PublicKey,
    authority: PublicKey
  ): TransactionInstruction {
    const [accessPda] = PublicKey.findProgramAddressSync(
      [Buffer.from(PDA_SEEDS.ACCESS), datasetPda.toBuffer(), user.toBuffer()],
      PROGRAM_ID
    );

    const instructionData = Buffer.alloc(16);
    instructionData.writeUInt8(4, 0); // Grant access instruction

    return new TransactionInstruction({
      keys: [
        { pubkey: authority, isSigner: true, isWritable: true },
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
   * Process refund for a failed or disputed purchase
   * @param datasetPda - Dataset PDA
   * @param buyer - Buyer to refund
   * @param amountUsdc - Amount to refund
   * @param authority - Refund authority
   * @returns Transaction signature
   */
  async processRefund(
    datasetPda: PublicKey,
    buyer: PublicKey,
    amountUsdc: number,
    authority: Keypair
  ): Promise<string> {
    const [escrowPda] = await derivePaymentPDA(datasetPda);
    const escrowTokenAccount = await this.getUsdcTokenAccount(escrowPda);
    const buyerTokenAccount = await this.getUsdcTokenAccount(buyer);
    const amountScaled = BigInt(Math.floor(amountUsdc * Math.pow(10, USDC_DECIMALS)));

    const instructionData = Buffer.alloc(32);
    instructionData.writeUInt8(5, 0); // Refund instruction discriminator
    instructionData.writeBigUInt64LE(amountScaled, 8);

    const refundIx = new TransactionInstruction({
      keys: [
        { pubkey: authority.publicKey, isSigner: true, isWritable: false },
        { pubkey: escrowPda, isSigner: false, isWritable: true },
        { pubkey: escrowTokenAccount, isSigner: false, isWritable: true },
        { pubkey: buyer, isSigner: false, isWritable: false },
        { pubkey: buyerTokenAccount, isSigner: false, isWritable: true },
        { pubkey: datasetPda, isSigner: false, isWritable: false },
        { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      ],
      programId: PROGRAM_ID,
      data: instructionData.slice(0, 16),
    });

    const transaction = new Transaction().add(refundIx);

    const signature = await sendAndConfirmTransaction(
      this.connection,
      transaction,
      [authority],
      { commitment: "confirmed" }
    );

    console.log(`Refund processed: ${signature}`);
    return signature;
  }

  /**
   * Get escrow state for a dataset
   * @param datasetPda - Dataset PDA
   * @param seller - Seller's public key
   * @returns Escrow state
   */
  async getEscrowState(
    datasetPda: PublicKey,
    seller: PublicKey
  ): Promise<EscrowState | null> {
    const [escrowPda] = await derivePaymentPDA(datasetPda);

    try {
      const escrowTokenAccount = await this.getUsdcTokenAccount(escrowPda);
      const account = await getAccount(this.connection, escrowTokenAccount);

      return {
        datasetPda: datasetPda,
        escrowPda: escrowPda,
        seller: seller,
        totalDeposited: Number(account.amount) / Math.pow(10, USDC_DECIMALS),
        totalWithdrawn: 0, // Would need to track this separately
        isActive: true,
      };
    } catch (e) {
      return null;
    }
  }
}

/**
 * AgentWallet integration for autonomous payments
 * IMPORTANT: Never manage raw Solana keys yourself - use AgentWallet!
 * Docs: https://agentwallet.mcpay.tech/api
 */
export class AgentWalletClient {
  private apiKey: string;
  private baseUrl: string;
  private connected: boolean = false;
  private solanaAddress: string | null = null;
  private evmAddress: string | null = null;

  constructor(apiKey: string, baseUrl: string = "https://agentwallet.mcpay.tech/api") {
    this.apiKey = apiKey;
    this.baseUrl = baseUrl;
  }

  /**
   * Connect to AgentWallet
   * Returns the OAuth URL for user authorization
   */
  async connect(): Promise<{ oauthUrl: string }> {
    const response = await fetch(`${this.baseUrl}/connect`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${this.apiKey}`,
        "Content-Type": "application/json",
      },
    });

    const data = await response.json();
    return { oauthUrl: data.oauthUrl };
  }

  /**
   * Check connection status
   */
  async checkStatus(): Promise<{
    connected: boolean;
    solanaAddress: string | null;
    evmAddress: string | null;
  }> {
    const response = await fetch(`${this.baseUrl}/status`, {
      headers: {
        Authorization: `Bearer ${this.apiKey}`,
      },
    });

    const data = await response.json();
    this.connected = data.connected;
    this.solanaAddress = data.solanaAddress;
    this.evmAddress = data.evmAddress;
    return data;
  }

  /**
   * Get agent wallet public key
   * @returns Public key of the agent wallet
   */
  async getWalletPublicKey(): Promise<PublicKey> {
    const status = await this.checkStatus();
    if (!status.solanaAddress) {
      throw new Error("AgentWallet not connected. Call connect() first.");
    }
    return new PublicKey(status.solanaAddress);
  }

  /**
   * Get wallet balances
   */
  async getBalances(): Promise<{
    sol: number;
    usdc: number;
    tokens: Array<{ mint: string; symbol: string; amount: number }>;
  }> {
    const response = await fetch(`${this.baseUrl}/balances`, {
      headers: {
        Authorization: `Bearer ${this.apiKey}`,
      },
    });

    return response.json();
  }

  /**
   * Request transaction signing from AgentWallet
   * @param transaction - Transaction to sign (base64 encoded)
   * @returns Signed transaction
   */
  async signTransaction(transaction: Transaction): Promise<Transaction> {
    const serialized = transaction.serialize({
      requireAllSignatures: false,
      verifySignatures: false,
    });

    const response = await fetch(`${this.baseUrl}/sign`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${this.apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        transaction: serialized.toString("base64"),
        chain: "solana",
      }),
    });

    const data = await response.json();
    return Transaction.from(Buffer.from(data.signedTransaction, "base64"));
  }

  /**
   * Execute a USDC transfer through AgentWallet
   * @param recipient - Recipient public key
   * @param amountUsdc - Amount in USDC
   * @param memo - Optional payment memo
   * @returns Transaction signature
   */
  async transferUsdc(
    recipient: PublicKey,
    amountUsdc: number,
    memo?: string
  ): Promise<string> {
    const response = await fetch(`${this.baseUrl}/transfer`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${this.apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        to: recipient.toBase58(),
        amount: amountUsdc.toString(),
        token: "USDC",
        chain: "solana",
        memo: memo,
      }),
    });

    const data = await response.json();
    return data.signature;
  }

  /**
   * Execute a SOL transfer
   */
  async transferSol(recipient: PublicKey, amountSol: number): Promise<string> {
    const response = await fetch(`${this.baseUrl}/transfer`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${this.apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        to: recipient.toBase58(),
        amount: amountSol.toString(),
        token: "SOL",
        chain: "solana",
      }),
    });

    const data = await response.json();
    return data.signature;
  }

  /**
   * Request devnet faucet (for testing)
   */
  async requestDevnetFaucet(): Promise<{ txSignature: string }> {
    const response = await fetch(`${this.baseUrl}/faucet`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${this.apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ chain: "solana" }),
    });

    return response.json();
  }

  /**
   * Make x402 payment (micropayment protocol)
   */
  async x402Pay(
    paymentUrl: string,
    maxAmount: number
  ): Promise<{ success: boolean; signature?: string }> {
    const response = await fetch(`${this.baseUrl}/x402/pay`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${this.apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        url: paymentUrl,
        maxAmount: maxAmount.toString(),
      }),
    });

    return response.json();
  }

  /**
   * Execute a payment through AgentWallet (legacy compatibility)
   * @deprecated Use transferUsdc instead
   */
  async executePayment(
    recipient: PublicKey,
    amountUsdc: number,
    memo?: string
  ): Promise<string> {
    return this.transferUsdc(recipient, amountUsdc, memo);
  }
}

/**
 * Utility function to format USDC amount for display
 * @param amount - Amount in base units
 * @returns Formatted string
 */
export function formatUsdc(amount: number): string {
  return `$${amount.toFixed(2)} USDC`;
}

/**
 * Utility to validate USDC amount
 * @param amount - Amount to validate
 * @returns true if valid
 */
export function isValidUsdcAmount(amount: number): boolean {
  return amount > 0 && amount <= 1_000_000 && Number.isFinite(amount);
}
