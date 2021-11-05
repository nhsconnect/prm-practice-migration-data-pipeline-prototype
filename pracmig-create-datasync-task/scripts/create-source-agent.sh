# Helper for creating the source agent stack

while getopts i: flag
do
    case "${flag}" in
        i) id=${OPTARG};;
    esac
done

aws cloudformation create-stack --template-body "$(cat ./source-supplier.yml)" --capabilities CAPABILITY_NAMED_IAM --timeout-in-minutes 30 --stack-name "source-supplier-$id" --disable-rollback