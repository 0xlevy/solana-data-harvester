import { NextRequest, NextResponse } from 'next/server';

// Mock dataset storage
const datasets: Map<string, any> = new Map();

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const datasetId = searchParams.get('id');

  if (datasetId) {
    const dataset = datasets.get(datasetId);
    if (!dataset) {
      return NextResponse.json(
        { error: 'Dataset not found' },
        { status: 404 }
      );
    }
    return NextResponse.json(dataset);
  }

  // Return all available datasets
  return NextResponse.json({
    datasets: Array.from(datasets.values()),
    count: datasets.size,
  });
}

export async function POST(request: NextRequest) {
  try {
    const data = await request.json();
    const datasetId = data.dataset_id || `dataset_${Date.now()}`;

    datasets.set(datasetId, {
      ...data,
      id: datasetId,
      created_at: new Date().toISOString(),
    });

    return NextResponse.json({
      success: true,
      dataset_id: datasetId,
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to create dataset' },
      { status: 500 }
    );
  }
}
