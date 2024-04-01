class GuiCredentialFieldException : Exception {
    [string] $additionalData

    GuiCredentialFieldException($Message, $additionalData) : base($Message) {
        $this.additionalData = $additionalData
    }
}

function Do-Main {
    Param
    (
         [Parameter(Mandatory=$true, Position=0)]
         [ValidatePattern('^*.xml')]
         [string]  $path_to_file,
         [Parameter(Mandatory=$true, Position=1)]
         [string] $prompt_message,
         [Parameter(Mandatory=$true, Position=2)]
         [AllowEmptyString()]
         [string] $user_name,
         [Parameter(Mandatory=$false)]
         [System.Management.Automation.PSCredential] $Credentials
    )
    $Credentials = Get-Credential -Message $prompt_message -UserName $user_name
    if ($Credentials) {
        $Credentials = $Credentials
    } else {
        # TODO: change second argument of Exception
        throw [GuiCredentialFieldException]::new("Gui credentials doesn't entered correctly.", "")
    }
    Export-Clixml -Path $path_to_file -InputObject $Credentials
}
