import { NextRequest, NextResponse } from 'next/server';

// In-memory store for metrics (in production, use a database)
let latestMetrics: any = null;

export async function GET() {
  if (!latestMetrics) {
    return NextResponse.json(
      { error: 'No metrics available yet' },
      { status: 404 }
    );
  }

  return NextResponse.json(latestMetrics);
}

export async function POST(request: NextRequest) {
  try {
    const data = await request.json();
    
    latestMetrics = {
      ...data,
      received_at: new Date().toISOString(),
    };

    console.log('[API] Received new metrics:', latestMetrics.timestamp);

    return NextResponse.json({ 
      success: true, 
      message: 'Metrics updated successfully' 
    });
  } catch (error) {
    console.error('[API] Error processing metrics:', error);
    return NextResponse.json(
      { error: 'Failed to process metrics' },
      { status: 500 }
    );
  }
}
