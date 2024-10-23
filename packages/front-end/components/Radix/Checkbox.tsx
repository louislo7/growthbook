import { Flex, Text, Checkbox as RadixCheckbox } from "@radix-ui/themes";
import { MarginProps } from "@radix-ui/themes/dist/cjs/props/margin.props";
import clsx from "clsx";
import { ReactElement } from "react";
import { Responsive } from "@radix-ui/themes/dist/cjs/props";
import HelperText, { getRadixColor } from "@/components/Radix/HelperText";

export type Size = "md" | "lg";

export function getRadixSize(size: Size): Responsive<"2" | "3"> {
  switch (size) {
    case "md":
      return "2";
    case "lg":
      return "3";
  }
}

export type Props = {
  label: string | ReactElement;
  disabled?: boolean;
  value: boolean;
  size?: Size;
  error?: string;
  errorLevel?: "error" | "warning";
  description?: string;
  setValue: (value: boolean) => void;
} & MarginProps;

export default function Checkbox({
  label,
  disabled,
  value,
  size = "md",
  setValue,
  description,
  error,
  errorLevel = "error",
  ...containerProps
}: Props) {
  const checkboxColor = error ? getRadixColor(errorLevel) : "violet";

  return (
    <Text
      as="label"
      size="2"
      className={clsx("rt-CheckboxItem", {
        "rt-TextDisabled": disabled,
        disabled: disabled,
      })}
      {...containerProps}
    >
      <Flex gap="2">
        <RadixCheckbox
          checked={value}
          onCheckedChange={(v) => setValue(v === true)}
          disabled={disabled}
          color={checkboxColor}
          size={getRadixSize(size)}
        />
        <Flex direction="column" gap="1">
          <Text weight="bold" className="main-text">
            {label}
          </Text>
          {description && <Text>{description}</Text>}
          {error && <HelperText status={errorLevel}>{error}</HelperText>}
        </Flex>
      </Flex>
    </Text>
  );
}