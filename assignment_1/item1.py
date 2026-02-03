from datetime import datetime
import re
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DoubleType,
    ArrayType,
    TimestampType,
    LongType,
)
from pyspark.sql.functions import col, explode_outer


schema = StructType(
    [
        StructField("driver_ID", StringType(), True),
        StructField("customer_id", LongType(), True),
        StructField(
            "transactionRecord",
            StructType(
                [
                    StructField("transaction_id", StringType(), True),
                    StructField(
                        "trip_info",
                        StructType(
                            [
                                StructField("trip_id", StringType(), True),
                                StructField(
                                    "pricing",
                                    StructType(
                                        [
                                            StructField(
                                                "base_fare", DoubleType(), True
                                            ),
                                            StructField(
                                                "route_data",
                                                StructType(
                                                    [
                                                        StructField(
                                                            "route_name",
                                                            StringType(),
                                                            True,
                                                        ),
                                                        StructField(
                                                            "segments",
                                                            ArrayType(
                                                                StructType(
                                                                    [
                                                                        StructField(
                                                                            "SEGMENT_ID",
                                                                            StringType(),
                                                                            True,
                                                                        ),
                                                                        StructField(
                                                                            "_Metrics",
                                                                            ArrayType(
                                                                                StructType(
                                                                                    [
                                                                                        StructField(
                                                                                            "metricValue",
                                                                                            DoubleType(),
                                                                                            True,
                                                                                        )
                                                                                    ]
                                                                                )
                                                                            ),
                                                                            True,
                                                                        ),
                                                                    ]
                                                                )
                                                            ),
                                                            True,
                                                        ),
                                                    ]
                                                ),
                                                True,
                                            ),
                                        ]
                                    ),
                                    True,
                                ),
                            ]
                        ),
                        True,
                    ),
                    StructField("createdAt", TimestampType(), True),
                ]
            ),
            True,
        ),
        StructField("COORDINATES", ArrayType(ArrayType(ArrayType(DoubleType()))), True),
    ]
)

data = [
    {
        "driver_ID": "DRV_1001",
        "customer_id": 9876543210,
        "transactionRecord": {
            "transaction_id": "TXN_A4B5C6D7",
            "trip_info": {
                "trip_id": "TRIP_XYZ789",
                "pricing": {
                    "base_fare": 15.50,
                    "route_data": {
                        "route_name": "Downtown to Airport Express",
                        "segments": [
                            {
                                "SEGMENT_ID": "SEG_001",
                                "_Metrics": [
                                    {"metricValue": 5.2},
                                    {"metricValue": 1.1},
                                    {"metricValue": 0.5},
                                ],
                            },
                            {
                                "SEGMENT_ID": "SEG_002",
                                "_Metrics": [
                                    {"metricValue": 12.8},
                                    {"metricValue": 3.4},
                                ],
                            },
                        ],
                    },
                },
            },
            "createdAt": datetime.now(),
        },
        "COORDINATES": [
            [[100.5018, 13.7563], [100.5500, 13.8000]],
            [[100.6000, 13.8500], [100.6500, 13.9000]],
        ],
    }
]

spark = SparkSession.builder.appName("item1").getOrCreate()
df = spark.createDataFrame(data=data, schema=schema)
df.show(truncate=False)
df.printSchema()


def flatten_df(df: DataFrame) -> DataFrame:
    """
    Recursively flattens a Spark DataFrame:
    - StructType columns are flattened
    - ArrayType columns are NOT exploded (preserves row count)

    Args:
        df: Input Spark DataFrame to flatten

    Returns:
        Flattened Spark DataFrame with preserved row count
    """
    complex_fields = True

    while complex_fields:
        complex_fields = False

        for field in df.schema.fields:
            field_name = field.name
            field_type = field.dataType

            # Flatten ONLY StructType
            if isinstance(field_type, StructType):
                complex_fields = True

                expanded_cols = [
                    col(f"{field_name}.{nested.name}").alias(
                        f"{field_name}_{nested.name}"
                    )
                    for nested in field_type.fields
                ]

                df = df.select("*", *expanded_cols).drop(field_name)
                break

    return df


def to_snake_case(name: str) -> str:
    name = re.sub(
        "(.)([A-Z][a-z]+)", r"\1_\2", name
    )  # Handle lower-to-upper case transitions
    name = re.sub(
        "([a-z0-9])([A-Z])", r"\1_\2", name
    )  # Handle lower/number-to-upper case transitions
    return name.replace(
        ".", "_"
    ).lower()  # Replace dots with underscores and convert to lowercase


def flatten_and_rename_to_snake_case(df: DataFrame) -> DataFrame:
    """
    Flattens a Spark DataFrame and renames all columns to snake_case format.

    Args:
        df: Input Spark DataFrame to flatten and rename

    Returns:
        Flattened DataFrame with snake_case column names
    """

    flat_df = flatten_df(df)

    renamed_cols = [col(c).alias(to_snake_case(c)) for c in flat_df.columns]

    return flat_df.select(*renamed_cols)


new_df = flatten_and_rename_to_snake_case(df=df)
new_df.show(truncate=False)
new_df.printSchema()
